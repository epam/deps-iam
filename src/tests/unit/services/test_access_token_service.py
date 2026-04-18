import pytest

from deps_iam.domain.exceptions import AuthError

token = "Bearer token"

expected_userinfo = {"sub": "usermale", "email": "good@mail.com", "first_name": "vin", "last_name": "diesel"}


@pytest.fixture
def access_token_auth_service(application):
    yield application.infrastructure_services.access_token_auth_service()


def test_access_token_service__valid_token__successful(mocker, access_token_auth_service):
    access_token_auth_service.get_userinfo = mocker.Mock(return_value=expected_userinfo)
    res = access_token_auth_service.get_userinfo({"Authorization": token})
    assert res == expected_userinfo


def test_access_token_service__invalid_token__raise_error(access_token_auth_service):
    with pytest.raises(AuthError):
        access_token_auth_service.get_userinfo({"Authorization": "glamour_bearer"})
