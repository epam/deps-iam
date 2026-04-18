from abc import ABC, abstractmethod

from deps_iam.domain.dtos import (
    InvitationListFilter,
    OrganisationListFilter,
    OrganisationUpdate,
    UserListFilter,
)
from deps_iam.domain.entities import (
    ApprovalRequest,
    Invitation,
    Organisation,
    OrganisationPk,
    UserEntity,
)


class IOrganisationRepository(ABC):
    @abstractmethod
    def get(self, pk: OrganisationPk) -> Organisation:
        pass

    @abstractmethod
    def get_list(self, filtering: OrganisationListFilter) -> list[Organisation]:
        pass

    @abstractmethod
    def create(self, entity: Organisation) -> Organisation:
        pass

    @abstractmethod
    def delete(self, pk: OrganisationPk) -> None:
        pass

    @abstractmethod
    def get_by_name(self, org_name: str) -> Organisation:
        pass

    @abstractmethod
    def partial_update(self, pk: OrganisationPk, organisation_update: OrganisationUpdate) -> Organisation:
        pass

    @abstractmethod
    def add_user_to_organisation(self, pk: OrganisationPk, user_pk: str) -> None:
        pass

    @abstractmethod
    def get_organisation_users(self, pk: OrganisationPk, filtering: UserListFilter) -> list[UserEntity]:
        pass

    @abstractmethod
    def get_total_organisation_users_count(self, pk: OrganisationPk, filtering: UserListFilter) -> int:
        pass

    @abstractmethod
    def get_invitees(
        self,
        organisation_pk: OrganisationPk,
        filtering: InvitationListFilter,
    ) -> list[Invitation]:
        pass

    @abstractmethod
    def get_total_invitees_count(
        self,
        organisation_pk: OrganisationPk,
        filtering: InvitationListFilter,
    ) -> int:
        pass

    @abstractmethod
    def invite_user_to_organisation(
        self, inviter_pk: str, organisation_pk: OrganisationPk, invitation: Invitation
    ) -> Invitation:
        pass

    @abstractmethod
    def delete_invitation(self, organisation_pk: OrganisationPk, user_email: str) -> None:
        pass

    @abstractmethod
    def create_approval_request(self, organisation_pk: OrganisationPk, user_pk: str) -> ApprovalRequest:
        pass

    @abstractmethod
    def delete_user_from_organisation(self, pk: OrganisationPk, user_pk: str) -> str:
        pass

    @abstractmethod
    def delete_approval_request(self, pk: OrganisationPk, user_pk: str) -> str:
        pass

    @abstractmethod
    def get_waiting_for_approvals(self, organisation_pk: OrganisationPk, filtering: UserListFilter) -> list[UserEntity]:
        pass

    @abstractmethod
    def get_total_approvals_count(self, organisation_pk: OrganisationPk, filtering: UserListFilter) -> int:
        pass
