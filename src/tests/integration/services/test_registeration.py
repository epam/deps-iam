import pytest

from deps_iam.domain.exceptions.registration import RegisterError

user_credentials = {
    "subject": "abc",
    "email": "purple_boy@test.ru",
    "first_name": "purple",
    "last_name": "boy",
    "organisation": "gov_domain",
}


@pytest.fixture
def register_service(services):
    return services.registration()


class TestRegistrationService:
    def test_register_new_user_valid_cred__successful(self, register_service, users_service):
        register_service.register_user(user_credentials, is_personal=True)
        new_user = users_service.get_user_by_email(user_credentials["email"])
        assert new_user.pk == user_credentials["subject"]
        assert new_user.email == user_credentials["email"]
        assert new_user.organisation == user_credentials["organisation"]

    def test_registration__only_main_creds__successful(self, register_service, users_service):
        user_credentials = {
            "subject": "sub",
            "email": "valid@email.by",
            "first_name": None,
            "last_name": None,
            "organisation": None,
        }
        register_service.register_user(user_credentials, is_personal=True)
        new_user = users_service.get_user_by_email(user_credentials["email"])
        assert new_user.pk == user_credentials["subject"]
        assert new_user.email == user_credentials["email"]
        assert new_user.organisation == user_credentials["organisation"]

    def test_register_new_user__invalid_email__raise_error(self, register_service):
        with pytest.raises(RegisterError):
            register_service.register_user({"email": "fAkE_emAil@"}, is_personal=True)

    def test_registration__valid_email__no_errors(self, register_service):
        register_service._validate_userinfo({"email": "che-email@benus.ex"})

    @pytest.mark.parametrize("email", [{"email": None}, {"email": ""}, {"email": "broken@email.u"}])
    def test_registration__invalid_email__raise_error(self, register_service, email):
        with pytest.raises(RegisterError):
            register_service._validate_userinfo(email)
