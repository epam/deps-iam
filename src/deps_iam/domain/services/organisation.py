import contextlib

from deps_iam import constants
from deps_iam.domain.dtos import (
    ExpandedUser,
    InvitationListFilter,
    ListDataObject,
    ListMetaDataObject,
    OrganisationListFilter,
    OrganisationUpdate,
    UserListFilter,
    UserUpdateObject,
)
from deps_iam.domain.entities import (
    Invitation,
    Organisation,
    OrganisationPk,
    UserEntity,
)
from deps_iam.domain.events import (
    OrganisationCreated,
    SendInvitationEmailEvent,
    TenantCreated,
)
from deps_iam.domain.exceptions import (
    ApprovalRequestAlreadyExistsError,
    ApprovalRequestNotFoundError,
    InvitationNotFoundError,
    OrganisationForbiddenError,
    UserNotFoundError,
    UserOrganisationNotFoundError,
)
from deps_iam.domain.interfaces.services import IOrganisationService, IUserService
from deps_iam.infrastructure.uow import UnitOfWork


class OrganisationService(IOrganisationService):
    def __init__(
        self,
        uow: UnitOfWork,
        user_service: IUserService,
    ):
        self._user_service = user_service
        self._uow = uow

    def create_organisation(self, organisation_entity: Organisation) -> Organisation:
        with self._uow:
            res = self._uow.organisation.create(organisation_entity)
            self._uow.event_publisher.publish(
                aggregate_type=constants.DOCUMENTS_EXCHANGER,
                aggregate_id="None",
                domain_events=[
                    OrganisationCreated(
                        id=res.pk,
                        organisation_name=organisation_entity.name,
                        personal=organisation_entity.is_personal,
                    ),
                ],
            )

            if not organisation_entity.is_personal:
                self._uow.event_publisher.publish(
                    aggregate_type=constants.TENANT_EXCHANGER,
                    aggregate_id="None",
                    domain_events=[
                        TenantCreated(tenant_id=res.pk),
                    ],
                )

            self._uow.commit()

        return res

    def get_organisation(self, pk: OrganisationPk) -> Organisation:
        with self._uow:
            return self._uow.organisation.get(pk)

    def delete_organisation(self, pk: OrganisationPk) -> bool:
        with self._uow:
            res = self._uow.organisation.delete(pk)
            self._uow.commit()

        return res

    def get_organisation_list(self, filtering: OrganisationListFilter) -> list[Organisation]:
        with self._uow:
            return self._uow.organisation.get_list(filtering)

    def get_organisation_by_name(self, org_name: str) -> Organisation:
        with self._uow:
            return self._uow.organisation.get_by_name(org_name)

    def partial_update(self, pk: OrganisationPk, organisation_update: OrganisationUpdate) -> Organisation:
        with self._uow:
            res = self._uow.organisation.partial_update(pk, organisation_update)
            self._uow.commit()

        return res

    def add_user_to_organisation(self, organisation_pk: OrganisationPk, user_pk: str) -> None:
        with self._uow:
            self._uow.organisation.add_user_to_organisation(organisation_pk, user_pk)
            self._uow.commit()

    def activate_user_organisation(self, organisation_pk: OrganisationPk, user_pk: str) -> Organisation:
        with self._uow:  # type: ignore
            user_organisation_pks = [
                org.pk for org in self._uow.organisation.get_list(OrganisationListFilter(user_pk=user_pk))  # type: ignore
            ]
            if organisation_pk not in user_organisation_pks:
                raise UserOrganisationNotFoundError(f"User {user_pk} hasn't available organisation: {organisation_pk}")

            self._uow.user.update(user_pk, UserUpdateObject(organisation=organisation_pk))
            self._uow.commit()
        return self._uow.organisation.get(organisation_pk)

    def get_organisation_users(self, pk: OrganisationPk, filtering: UserListFilter) -> ListDataObject[UserEntity]:
        with self._uow:
            total = self._uow.organisation.get_total_organisation_users_count(pk, filtering)

            organisation_users = self._uow.organisation.get_organisation_users(pk, filtering)

            user_list = ListDataObject[UserEntity](
                meta=ListMetaDataObject(total=total, size=len(organisation_users)),
                result=organisation_users,
            )
            self._uow.commit()

        return user_list

    def get_invitees(
        self, organisation_pk: OrganisationPk, filtering: InvitationListFilter
    ) -> ListDataObject[Invitation]:
        with self._uow:
            count = self._uow.organisation.get_total_invitees_count(organisation_pk, filtering)
            invitees = self._uow.organisation.get_invitees(organisation_pk, filtering)
        return ListDataObject(meta=ListMetaDataObject(total=count, size=len(invitees)), result=invitees)

    def invite_users_to_organisation(
        self, inviter_pk: str, organisation_pk: OrganisationPk, invitations: list[Invitation]
    ) -> list[Invitation]:
        invited_users = []
        with self._uow:
            for invitation in invitations:
                try:
                    user = self._uow.user.get_user_by_email(invitation.email)
                    if not self._is_user_in_organisation(organisation_pk, user.pk):
                        self.add_user_to_organisation(organisation_pk, user.pk)
                        with contextlib.suppress(ApprovalRequestNotFoundError):
                            self._uow.organisation.delete_approval_request(organisation_pk, user.pk)
                except UserNotFoundError:
                    if not self._is_user_invited_to_organisation(organisation_pk, invitation.email):
                        res = self._uow.organisation.invite_user_to_organisation(
                            inviter_pk, organisation_pk, invitation
                        )
                        invited_users.append(res)
                self._publish_send_invitation_email_event(invitation.email, inviter_pk, organisation_pk)
            self._uow.commit()

        return invited_users

    def _is_user_in_organisation(self, organisation_pk: OrganisationPk, user_pk: str) -> bool:
        already_added = self._uow.organisation.get_organisation_users(organisation_pk, UserListFilter(pks=[user_pk]))
        return bool(already_added)

    def _is_user_invited_to_organisation(self, organisation_pk: OrganisationPk, email: str) -> bool:
        invited = self._uow.organisation.get_invitees(
            organisation_pk,
            InvitationListFilter(search_term=email),
        )
        return bool(invited)

    def _publish_send_invitation_email_event(
        self, user_email: str, inviter_pk: str, organisation_pk: OrganisationPk
    ) -> None:
        inviter = self._uow.user.get(inviter_pk)
        inviter_name = f"{inviter.first_name} {inviter.last_name}"
        self._uow.event_publisher.publish(
            aggregate_type=constants.DOCUMENTS_EXCHANGER,
            aggregate_id="None",
            domain_events=[
                SendInvitationEmailEvent(
                    user_email=user_email,
                    inviter_name=inviter_name,
                    organisation=organisation_pk,
                ),
            ],
        )

    def join_organisation(self, organisation_pk: OrganisationPk, user_pk: str, user_email: str) -> ExpandedUser:
        with self._uow:
            try:
                self.activate_user_organisation(organisation_pk, user_pk)
            except UserOrganisationNotFoundError:
                self._uow.organisation.get(organisation_pk)  # checks if organisation exists at all
                try:  # noqa: WPS505
                    self._uow.organisation.delete_invitation(organisation_pk, user_email)
                    self._uow.organisation.add_user_to_organisation(organisation_pk, user_pk)
                    self.activate_user_organisation(organisation_pk, user_pk)
                except InvitationNotFoundError:
                    with contextlib.suppress(ApprovalRequestAlreadyExistsError):
                        self._uow.organisation.create_approval_request(organisation_pk, user_pk)
                        self._uow.commit()
                    raise OrganisationForbiddenError("Forbidden to join organisation: user wasn't invited")

            self._uow.commit()
            return self._user_service.get_expanded_user(user_pk)

    def _is_all_users_deletion(self, organisation_pk: OrganisationPk, user_pks: list[str]) -> bool:
        organisation_users_count = self._uow.organisation.get_total_organisation_users_count(
            organisation_pk, UserListFilter()
        )
        return len(user_pks) >= organisation_users_count

    def delete_user_from_organisation(self, organisation_pk: OrganisationPk, user_pks: list[str]) -> list[str]:
        with self._uow:
            if self._is_all_users_deletion(organisation_pk, user_pks):
                raise OrganisationForbiddenError("Can't delete all users of organisation.")

            deleted_users_pks = []
            for user_pk in user_pks:
                self._uow.organisation.delete_user_from_organisation(organisation_pk, user_pk)
                deleted_users_pks.append(user_pk)

                if self._uow.user.get(user_pk).organisation != organisation_pk:
                    continue

                user_organisations = self._uow.organisation.get_list(OrganisationListFilter(user_pk=user_pk))
                if user_organisations:
                    self._uow.user.update(user_pk, UserUpdateObject(organisation=user_organisations[0].pk))
                else:
                    self._uow.user.deactivate_user_organisation(user_pk)

            self._uow.commit()

        return deleted_users_pks

    def approve_user_request(self, organisation_pk: OrganisationPk, user_pks: list[str]) -> list[str]:
        with self._uow:
            approved_users_pks = []
            for user_pk in user_pks:
                self._uow.organisation.delete_approval_request(organisation_pk, user_pk)
                self._uow.organisation.add_user_to_organisation(organisation_pk, user_pk)
                self.activate_user_organisation(organisation_pk, user_pk)
                approved_users_pks.append(user_pk)
            self._uow.commit()

        return approved_users_pks

    def get_waiting_for_approvals(
        self, organisation_pk: OrganisationPk, filtering: UserListFilter
    ) -> ListDataObject[UserEntity]:
        with self._uow:
            count = self._uow.organisation.get_total_approvals_count(organisation_pk, filtering)
            users = self._uow.organisation.get_waiting_for_approvals(organisation_pk, filtering)
            return ListDataObject(result=users, meta=ListMetaDataObject(total=count, size=len(users)))

    def decline_user_request(self, organisation_pk: OrganisationPk, user_pks: list[str]) -> list[str]:
        with self._uow:
            declined_users_pks = []
            for user_pk in user_pks:
                declined_user_pk = self._uow.organisation.delete_approval_request(organisation_pk, user_pk)
                declined_users_pks.append(declined_user_pk)
            self._uow.commit()

        return declined_users_pks

    def delete_invitees(self, organisation_pk: OrganisationPk, invitees: list[str]) -> None:
        with self._uow:
            for invitee in invitees:
                self._uow.organisation.delete_invitation(organisation_pk, invitee)
            self._uow.commit()
