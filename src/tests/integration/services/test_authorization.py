import json

import pytest

from deps_iam import constants
from deps_iam.domain.exceptions import IAMException
from deps_iam.extras.auth.deps_auth import AUTH_HEADER

token_string = "Bearer token"

expected_userinfo_response = {
    "sub": "user1",
    "email": "user@email.com",
    "given_name": "first_name",
    "family_name": "last_name",
}


@pytest.fixture
def auth_mock(services):
    services.authorization.reset_override()
    return services.authorization()


class TestAuthorizationService:
    def test_create__new_token__return_token(self, authorization_service):
        user_credentials = {"name": "username"}
        result = authorization_service.create_access_token(user_credentials)

        assert type(result) == str

    def test_create__new_token_no_credentials__raise_error(self, authorization_service):
        user_credentials = {}

        with pytest.raises(IAMException):
            authorization_service.create_access_token(user_credentials)

    def test__map_deps_token_user_credentials__type(self, authorization_service):
        decoded_token = {
            "sub": "user1",
            "email": "email1",
            "roles": ["role1"],
            "organisation": "group1",
        }
        result = authorization_service._map_deps_token_user_credentials(decoded_token)
        assert type(result) == dict

    @pytest.mark.usefixtures("use_enable_personal_org")
    def test__authorize__type(self, mocker, authorization_service):
        authorization_service._access_token_auth_servie = mocker.Mock()
        authorization_service._access_token_auth_servie.get_userinfo.return_value = expected_userinfo_response
        request_header = {AUTH_HEADER: token_string}
        result = authorization_service.authorize(request_header)
        assert type(result) == str

    def test__map_deps_token_user_credentials__empty_attrs(self, authorization_service):
        userinfo = {
            "sub": "user1",
            "email": "email1",
            "roles": ["role1"],
            "organisation": "group1",
        }
        result = authorization_service._map_deps_token_user_credentials(userinfo)
        assert all(
            (
                result["first_name"] is None,
                result["last_name"] is None,
            )
        )

    def test__map_deps_token_user_credentials__not_empty_attrs(self, authorization_service):
        userinfo = {
            "sub": "user1",
            "given_name": "first_name",
            "family_name": "last_name",
            "email": "email",
        }
        result = authorization_service._map_deps_token_user_credentials(userinfo)
        assert all(
            (
                result["email"] is not None,
                result["first_name"] is not None,
                result["last_name"] is not None,
            )
        )

    def test__map_deps_token_user_credentials__upper_case_email(self, authorization_service):
        decoded_token = {"sub": "user1", "roles": ["role1"], "organisation": "group1", "email": "Name_Surname@test.com"}
        result = authorization_service._map_deps_token_user_credentials(decoded_token)
        assert result["email"] == "name_surname@test.com"

    @pytest.mark.usefixtures("use_enable_personal_org")
    def test__enable_personal_org__filled_organisation(self, authorization_service, mocker):
        authorization_service._access_token_auth_servie = mocker.Mock()
        authorization_service._access_token_auth_servie.get_userinfo.return_value = expected_userinfo_response
        request_header = {AUTH_HEADER: token_string}
        result = json.loads(authorization_service.authorize(request_header))
        assert result["organisation"] is not None

    @pytest.mark.usefixtures("use_enable_personal_org")
    def test_authorize__org_created_event_published(
        self,
        authorization_service,
        users_service,
        monkeypatch,
        mocker,
        produced_messages,
    ):
        user_data = {
            "subject": "infinite coolness",
            "email": "test@outlook.com",
            "first_name": "Benedict",
            "last_name": "Cucumberbatch",
        }

        monkeypatch.setattr(
            authorization_service,
            "_get_user_credentials",
            mocker.Mock(return_value=user_data),
        )

        user_creds = json.loads(authorization_service.authorize(dict()))
        user = users_service.get_user_by_email(user_creds["email"])

        assert user_creds["subject"] == user_data["subject"]
        assert user_creds["organisation"] == user.organisation
        assert user_creds["email"] == user_data["email"]

        assert len(produced_messages) == 1

    @pytest.mark.usefixtures("use_enable_personal_org")
    def test_authorize__personal_org_enabled__personal_org_created(
        self,
        authorization_service,
        organisation_service,
        users_service,
        monkeypatch,
        mocker,
        produced_messages,
    ):
        authorization_service._publisher = mocker.Mock()
        subject = "test12344"
        user_data = {
            "subject": subject,
            "roles": ["regular everyday normal guy"],
            "organisation": subject,
            "email": "test@outlook.com",
            "first_name": "Benedict",
            "last_name": "Cucumberbatch",
        }

        monkeypatch.setattr(
            authorization_service,
            "_get_user_credentials",
            mocker.Mock(return_value=user_data),
        )

        user_creds = json.loads(authorization_service.authorize(dict()))
        user = users_service.get_user_by_email("test@outlook.com")
        org = organisation_service.get_organisation(user.organisation)

        assert user_creds["organisation"] == user.organisation
        assert (
            org.name == f"{user_data['first_name']} {user_data['last_name']} {constants.PERSONAL_ORGANISATION_POSTFIX}"
        )
        assert len(produced_messages) == 1

    def test__no_api_key_in_header__jwt_flow_called(self, authorization_service, monkeypatch, mocker):
        monkeypatch.setattr(
            authorization_service,
            "_get_user_credentials_from_oidc_provider",
            mocker.Mock(return_value={}),
        )
        authorization_service._get_user_credentials(request_headers={})
        authorization_service._get_user_credentials_from_oidc_provider.assert_called_once()

    @pytest.mark.usefixtures("use_api_key_auth_enabled")
    def test__ak_in_header__enable_ak_auth__api_key_flow_called(self, authorization_service, monkeypatch, mocker):
        monkeypatch.setattr(
            authorization_service,
            "_get_user_credentials_from_api_key",
            mocker.Mock(return_value={}),
        )
        authorization_service._get_user_credentials(request_headers={constants.API_KEY: "User api key"})
        authorization_service._get_user_credentials_from_api_key.assert_called_once()

    def test__ak_in_header__disable_ak_auth__access_token_flow_called(self, authorization_service, monkeypatch, mocker):
        monkeypatch.setattr(
            authorization_service,
            "_get_user_credentials_from_oidc_provider",
            mocker.Mock(return_value={}),
        )
        authorization_service._get_user_credentials(request_headers={constants.API_KEY: "User api key"})
        authorization_service._get_user_credentials_from_oidc_provider.assert_called_once()
