import pytest

from deps_iam import constants


@pytest.fixture
def register_service(services):
    services.registration.reset_override()
    yield services.registration()


class TestRegistrationService:
    def test_generate_organisation__personal__org_name_from_user_name(self, register_service):
        user_credentials = {
            "subject": "abc",
            "email": "email@test.ru",
            "first_name": "first-name",
            "last_name": "last-name",
            "organisation": "gov_domain",
        }

        org = register_service.generate_organisation(user_credentials, is_personal=True)

        assert org.pk == user_credentials["organisation"]
        assert (
            org.name
            == f"{user_credentials['first_name']} {user_credentials['last_name']} {constants.PERSONAL_ORGANISATION_POSTFIX}"
        )
        assert org.is_personal

    def test_generate_organisation__personal__org_name_from_user_email(self, register_service):
        user_credentials = {
            "email": "email@test.ru",
            "organisation": "gov_domain",
        }

        org = register_service.generate_organisation(user_credentials, is_personal=True)

        assert org.pk == user_credentials["organisation"]
        assert org.name == f"{user_credentials['email']} {constants.PERSONAL_ORGANISATION_POSTFIX}"
        assert org.is_personal

    def test_generate_organisation__not_personal__org_name_is_id(self, register_service):
        user_credentials = {
            "email": "email@test.ru",
            "organisation": "gov_domain",
        }

        org = register_service.generate_organisation(user_credentials, is_personal=False)

        assert org.pk == user_credentials["organisation"]
        assert org.name == user_credentials["organisation"]
        assert not org.is_personal
