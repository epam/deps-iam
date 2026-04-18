from abc import ABC, abstractmethod

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


class IOrganisationService(ABC):
    @abstractmethod
    def create_organisation(self, organisation_entity: Organisation) -> Organisation:
        ...

    @abstractmethod
    def get_organisation(self, pk: OrganisationPk) -> Organisation:
        ...

    @abstractmethod
    def delete_organisation(self, pk: OrganisationPk) -> bool:
        ...

    @abstractmethod
    def get_organisation_list(self, filtering: OrganisationListFilter) -> list[Organisation]:
        ...

    @abstractmethod
    def get_organisation_by_name(self, org_name: str) -> Organisation:
        ...

    @abstractmethod
    def partial_update(self, pk: OrganisationPk, organisation_update: OrganisationUpdate) -> Organisation:
        ...

    @abstractmethod
    def activate_user_organisation(self, organisation_pk: OrganisationPk, user_pk: str) -> Organisation:
        ...

    @abstractmethod
    def add_user_to_organisation(self, organisation_pk: OrganisationPk, user_pk: str) -> None:
        ...

    @abstractmethod
    def get_organisation_users(self, pk: OrganisationPk, filtering: UserListFilter) -> ListDataObject[UserEntity]:
        ...

    @abstractmethod
    def get_invitees(
        self, organisation_pk: OrganisationPk, filtering: InvitationListFilter
    ) -> ListDataObject[Invitation]:
        ...

    @abstractmethod
    def invite_users_to_organisation(
        self, inviter_pk: str, organisation_pk: OrganisationPk, invitations: list[Invitation]
    ) -> list[Invitation]:
        ...

    @abstractmethod
    def join_organisation(self, organisation_pk: OrganisationPk, user_pk: str, user_email: str) -> ExpandedUser:
        ...

    @abstractmethod
    def delete_user_from_organisation(self, organisation_pk: OrganisationPk, user_pks: list[str]) -> list[str]:
        ...

    @abstractmethod
    def approve_user_request(self, organisation_pk: OrganisationPk, user_pks: list[str]) -> list[str]:
        ...

    @abstractmethod
    def get_waiting_for_approvals(
        self, organisation_pk: OrganisationPk, filtering: UserListFilter
    ) -> ListDataObject[UserEntity]:
        ...

    @abstractmethod
    def decline_user_request(self, organisation_pk: OrganisationPk, user_pks: list[str]) -> list[str]:
        ...

    @abstractmethod
    def delete_invitees(self, organisation_pk: OrganisationPk, invitees: list[str]) -> None:
        ...
