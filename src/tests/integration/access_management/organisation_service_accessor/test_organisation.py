import pytest

from deps_iam.domain.dtos import OrganisationListFilter, OrganisationUpdate
from deps_iam.domain.exceptions import (
    OrganisationForbiddenError,
    UserOrganisationNotFoundError,
)
from deps_iam.infrastructure.access_management.context_vars import user


@pytest.mark.usefixtures("set_existing_user")
class TestOrganisationServiceAccessorForOrganisation:
    def test_create__organisation__no_exists__user_has_access_to_organisation(
        self,
        org_access_service,
        organisation_factory,
    ):
        org = org_access_service.create_organisation(organisation_factory())
        user_orgs = org_access_service.get_organisation_list(OrganisationListFilter())
        assert org in user_orgs

    def test_get_list_organisation__no_access__raise_error(
        self, org_access_service, organisation_factory, other_organisation_user
    ):
        org = org_access_service.create_organisation(organisation_factory())
        user.set(other_organisation_user)
        other_user_orgs = org_access_service.get_organisation_list(OrganisationListFilter())
        with pytest.raises(OrganisationForbiddenError):
            org_access_service.get_organisation(org.pk)
        assert org not in other_user_orgs

    def test_partial__has_access__successful(self, org_access_service, organisation_factory):
        org = org_access_service.create_organisation(organisation_factory())
        changed_org = org_access_service.partial_update(org.pk, OrganisationUpdate("CHANGED_NAME"))
        assert org.pk == changed_org.pk
        assert org.name != changed_org.name
        assert changed_org.name == "CHANGED_NAME"

    def test_partial_update__no_access__raise_error(
        self, org_access_service, organisation_factory, other_organisation_user
    ):
        org = org_access_service.create_organisation(organisation_factory())
        user.set(other_organisation_user)
        with pytest.raises(OrganisationForbiddenError):
            org_access_service.partial_update(org.pk, OrganisationUpdate("CHANGED_NAME"))

    def test_delete_organisation__has_access__successful(self, org_access_service, organisation_factory):
        org = org_access_service.create_organisation(organisation_factory())
        org_access_service.delete_organisation(org.pk)
        assert org not in org_access_service.get_organisation_list(OrganisationListFilter())

    def test_delete_organisation__no_access__raise_error(
        self, org_access_service, organisation_factory, other_organisation_user
    ):
        org = org_access_service.create_organisation(organisation_factory())
        user.set(other_organisation_user)
        with pytest.raises(OrganisationForbiddenError):
            org_access_service.delete_organisation(org.pk)

    def test_get_organisation_by_name__has_access__successful(self, org_access_service, organisation_factory):
        org = org_access_service.create_organisation(organisation_factory())
        res = org_access_service.get_organisation_by_name(org.name)
        assert org == res

    def test_get_organisation_by_name__no_access__raise_error(
        self, org_access_service, organisation_factory, other_organisation_user
    ):
        org = org_access_service.create_organisation(organisation_factory())
        user.set(other_organisation_user)
        with pytest.raises(OrganisationForbiddenError):
            org_access_service.get_organisation_by_name(org.name)

    def test_activate_user_organisation__has_access__successful(
        self,
        org_access_service,
        organisation_factory,
    ):
        user_ = user.get(None)
        org = org_access_service.create_organisation(organisation_factory())
        org_2 = org_access_service.create_organisation(organisation_factory())
        res = org_access_service.activate_user_organisation(org_2.pk, user_["subject"])
        assert all(org in (org_access_service.get_organisation_list(OrganisationListFilter())) for org in (org, org_2))
        assert org_2 == res

    def test_activate_user_organisation__no_access__raise_error(
        self, org_access_service, organisation_factory, other_organisation_user
    ):
        org = org_access_service.create_organisation(organisation_factory())
        user.set(other_organisation_user)
        with pytest.raises(UserOrganisationNotFoundError):
            org_access_service.activate_user_organisation(org.pk, other_organisation_user["subject"])
