import pytest

from deps_iam.domain.exceptions import OrganisationForbiddenError


@pytest.mark.usefixtures("set_existing_user", "add_user_to_organisation")
class TestOrganisationBasedOrganisationServiceAccessManager:
    def test_check_access__successful(self, org_access_manager, existing_user):
        org_access_manager.check_access(existing_user.organisation)

    def test_check_access__fails(self, org_access_manager):
        with pytest.raises(OrganisationForbiddenError):
            org_access_manager.check_access("test_org_pk")

    def test_user_has_several_org__check_access__successful(
        self, org_access_service, org_access_manager, organisation_factory
    ):
        new_org = org_access_service.create_organisation(organisation_factory())
        org_access_manager.check_access(new_org.pk)
