import pytest

from deps_iam.domain.exceptions import OrganisationForbiddenError


@pytest.mark.usefixtures("set_this_user")
class TestOrganisationBasedAccessManager:
    def test_check_access__has_access__success(
        self, organisation_repository_mock, organisation_factory, org_access_manager
    ):
        org = organisation_factory()
        organisation_repository_mock.get_list.return_value = [org]

        org_access_manager.check_access(org.pk)

    def test_check_access__no_access__raise_error(self, organisation_repository_mock, org_access_manager):
        organisation_repository_mock.get_list.side_effect = OrganisationForbiddenError

        with pytest.raises(OrganisationForbiddenError):
            org_access_manager.check_access("abc")

    def test_grant_access__success(self, organisation_repository_mock, org_access_manager):
        organisation_repository_mock.add_user_to_organisation.return_value = None

        org_access_manager.grant_access("efg")
