import contextlib

from deps_iam.domain.dtos import (
    ExpandedUser,
    InvitationListFilter,
    ListDataObject,
    OrganisationListFilter,
    OrganisationUpdate,
    UserListFilter,
)
from deps_iam.domain.entities import (
    Invitation,
    Organisation,
    OrganisationPk,
    UserEntity,
)
from deps_iam.domain.exceptions import UserNotFoundError
from deps_iam.domain.interfaces.access_managers import IOrganisationAccessManager
from deps_iam.domain.interfaces.services import IOrganisationService
from deps_iam.infrastructure.access_management.access_managers.user import (
    CurrentUserMixin,
)


class OrganisationServiceAccessor(IOrganisationService, CurrentUserMixin):
    def __init__(
        self,
        organisation_service: IOrganisationService,
        organisation_access_manager: IOrganisationAccessManager,
    ):
        self._org_service = organisation_service
        self._org_access_manager = organisation_access_manager

    def get_organisation(self, pk: OrganisationPk) -> Organisation:
        org = self._org_service.get_organisation(pk)
        self._org_access_manager.check_access(pk)
        return org

    def create_organisation(self, organisation_entity: Organisation) -> Organisation:
        org = self._org_service.create_organisation(organisation_entity)
        self._org_access_manager.grant_access(org.pk)

        return org

    def delete_organisation(self, pk: OrganisationPk) -> bool:
        self._org_access_manager.check_access(pk)
        return self._org_service.delete_organisation(pk)

    def get_organisation_list(self, filtering: OrganisationListFilter) -> list[Organisation]:
        with contextlib.suppress(UserNotFoundError):
            self._org_access_manager.patch_filter(filtering)
        return self._org_service.get_organisation_list(filtering)

    def get_organisation_by_name(self, org_name: str) -> Organisation:
        org = self._org_service.get_organisation_by_name(org_name)
        self._org_access_manager.check_access(org.pk)
        return org

    def partial_update(self, pk: OrganisationPk, organisation_update: OrganisationUpdate) -> Organisation:
        self._org_access_manager.check_access(pk)
        return self._org_service.partial_update(pk, organisation_update)

    def activate_user_organisation(self, organisation_pk: OrganisationPk, user_pk: str) -> Organisation:
        return self._org_service.activate_user_organisation(organisation_pk, user_pk)

    def add_user_to_organisation(self, organisation_pk: OrganisationPk, user_pk: str) -> None:
        return self._org_service.add_user_to_organisation(organisation_pk, user_pk)

    def get_organisation_users(self, pk: OrganisationPk, filtering: UserListFilter) -> ListDataObject[UserEntity]:
        self._org_access_manager.check_access(pk)
        return self._org_service.get_organisation_users(pk, filtering)

    def get_invitees(
        self, organisation_pk: OrganisationPk, filtering: InvitationListFilter
    ) -> ListDataObject[Invitation]:
        self._org_access_manager.check_access(organisation_pk)
        return self._org_service.get_invitees(organisation_pk, filtering)

    def invite_users_to_organisation(
        self, inviter_pk: str, organisation_pk: OrganisationPk, invitations: list[Invitation]
    ) -> list[Invitation]:
        self._org_access_manager.check_access(organisation_pk)
        return self._org_service.invite_users_to_organisation(inviter_pk, organisation_pk, invitations)

    def join_organisation(self, organisation_pk: OrganisationPk, user_pk: str, user_email: str) -> ExpandedUser:
        return self._org_service.join_organisation(organisation_pk, user_pk, user_email)

    def delete_user_from_organisation(self, organisation_pk: OrganisationPk, user_pks: list[str]) -> list[str]:
        self._org_access_manager.check_access(organisation_pk)
        return self._org_service.delete_user_from_organisation(organisation_pk, user_pks)

    def approve_user_request(self, organisation_pk: OrganisationPk, user_pks: list[str]) -> list[str]:
        self._org_access_manager.check_access(organisation_pk)
        return self._org_service.approve_user_request(organisation_pk, user_pks)

    def get_waiting_for_approvals(
        self, organisation_pk: OrganisationPk, filtering: UserListFilter
    ) -> ListDataObject[UserEntity]:
        self._org_access_manager.check_access(organisation_pk)
        return self._org_service.get_waiting_for_approvals(organisation_pk, filtering)

    def decline_user_request(self, organisation_pk: OrganisationPk, user_pks: list[str]) -> list[str]:
        self._org_access_manager.check_access(organisation_pk)
        return self._org_service.decline_user_request(organisation_pk, user_pks)

    def delete_invitees(self, organisation_pk: OrganisationPk, invitees: list[str]) -> None:
        self._org_access_manager.check_access(organisation_pk)
        return self._org_service.delete_invitees(organisation_pk, invitees)
