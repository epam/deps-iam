from typing import List, Optional

from sqlalchemy import asc, delete, desc, insert, join, update
from sqlalchemy.engine import Connection
from sqlalchemy.exc import StatementError
from sqlalchemy.sql import functions, select

from deps_iam.constants import PERSONAL_ORGANISATION_POSTFIX
from deps_iam.domain.dtos import (
    InvitationListFilter,
    InvitationSortingFieldEnum,
    OrganisationListFilter,
    OrganisationTypesEnum,
    OrganisationUpdate,
    PaginationObject,
    UserListFilter,
    UserSortingFieldsEnum,
)
from deps_iam.domain.entities import (
    ApprovalRequest,
    Invitation,
    Organisation,
    OrganisationPk,
    UserEntity,
)
from deps_iam.domain.exceptions import (
    ApprovalRequestAlreadyExistsError,
    ApprovalRequestNotFoundError,
    IAMException,
    InvitationAlreadyExistsError,
    InvitationNotFoundError,
    OrganisationAlreadyExistsError,
    OrganisationNotFoundError,
    UserOrganisationAlreadyExistsError,
    UserOrganisationNotFoundError,
)
from deps_iam.domain.interfaces.repositories import IOrganisationRepository
from deps_iam.extras.datasource import Database
from deps_iam.infrastructure.repositories.constants import DatabaseErrorTypeEnum
from deps_iam.infrastructure.repositories.error_extractor import (
    extract_database_error_type,
)
from deps_iam.infrastructure.repositories.organisation.mappers import (
    build_approval_request_from_dict,
    build_invitation_from_dict,
    build_organisation_dict,
    build_organisation_entities_from_dict,
    build_organisation_entity_from_dict,
    build_organisation_update_dict,
)
from deps_iam.infrastructure.repositories.user.mappers import build_user_from_dict
from deps_iam.infrastructure.tables import (
    approval_request_table,
    direct_invitation_table,
)
from deps_iam.infrastructure.tables.organisation import organisation_table
from deps_iam.infrastructure.tables.user import user_table
from deps_iam.infrastructure.tables.user_organisation import user_organisation_table


class OrganisationRepository(IOrganisationRepository):  # noqa: WPS214
    def __init__(self, database: Database) -> None:
        self._database = database

    def create(self, entity: Organisation) -> Organisation:
        organisation_object = build_organisation_dict(entity)
        insert_query = insert(organisation_table).values(**organisation_object).returning(organisation_table)

        try:
            res = self._connection.execute(insert_query).fetchone()
        except StatementError as err:
            if extract_database_error_type(err, self._database) == DatabaseErrorTypeEnum.UNIQUE_VIOLATION:
                raise OrganisationAlreadyExistsError(f"Organisation with {organisation_object['name']} name exists.")

            raise IAMException(str(err))

        return build_organisation_entity_from_dict(res)

    def get(self, organisation_pk: OrganisationPk) -> Organisation:
        query = select([organisation_table]).where(organisation_table.c.pk == organisation_pk)

        organisation_object_row = self._connection.execute(query).fetchone()

        if not organisation_object_row:
            raise OrganisationNotFoundError(f"Organisation with id {organisation_pk} not found.")

        return build_organisation_entity_from_dict(organisation_object_row)

    def get_by_name(self, organisation_name: str) -> Organisation:
        query = select([organisation_table]).where(organisation_table.c.name == organisation_name)

        organisation_object_row = self._connection.execute(query).fetchone()

        if not organisation_object_row:
            raise OrganisationNotFoundError(f"Organisation `{organisation_name}` not found.")

        return build_organisation_entity_from_dict(organisation_object_row)

    def get_list(self, filtering: Optional[OrganisationListFilter] = None) -> List[Organisation]:
        query = select([organisation_table])
        if filtering:
            query = self._filter_organisations(filtering, query)

        organisation_list_object_rows = self._connection.execute(query).fetchall()

        return build_organisation_entities_from_dict(organisation_list_object_rows)

    def delete(self, organisation_pk: OrganisationPk) -> None:
        query = delete(organisation_table).where(organisation_table.c.pk == organisation_pk)

        answer = self._connection.execute(query)

        if answer.rowcount == 0:
            raise OrganisationNotFoundError(f"Organisation with id {organisation_pk} was not found.")

    def update_organisation_name(self, organisation_pk: OrganisationPk, new_organisation_name: str) -> Organisation:
        query = (
            update(organisation_table)
            .where(organisation_table.c.pk == organisation_pk)
            .values(name=new_organisation_name)
            .returning(organisation_table)
        )

        organisation_object_row = self._connection.execute(query).fetchone()
        if not organisation_object_row:
            raise OrganisationNotFoundError(f"Organisation with pk {organisation_pk} not found.")
        return build_organisation_entity_from_dict(organisation_object_row)

    def partial_update(self, pk: OrganisationPk, organisation_update: OrganisationUpdate) -> Organisation:
        organisation_update_dict = build_organisation_update_dict(organisation_update)
        if organisation_update_dict:
            query = (
                update(organisation_table)
                .where(organisation_table.c.pk == pk)
                .values(**build_organisation_update_dict(organisation_update))
                .returning(organisation_table)
            )
            organisation_object_row = self._connection.execute(query).fetchone()
            if not organisation_object_row:
                raise OrganisationNotFoundError(f"Organisation with pk {pk} not found.")

            return build_organisation_entity_from_dict(organisation_object_row)
        return self.get(pk)

    def add_user_to_organisation(self, organisation_pk: OrganisationPk, user_pk: str) -> None:
        query = insert(user_organisation_table).values(organisation_pk=organisation_pk, user_pk=user_pk)
        try:
            self._connection.execute(query)
        except StatementError as err:
            if extract_database_error_type(err, self._database) == DatabaseErrorTypeEnum.UNIQUE_VIOLATION:
                raise UserOrganisationAlreadyExistsError(
                    f"Organisation with {organisation_pk} already exists for user: {user_pk}."
                )

            raise IAMException(str(err))

    def get_organisation_users(self, organisation_pk: OrganisationPk, filtering: UserListFilter) -> List[UserEntity]:
        query = self._get_organisation_users_query(organisation_pk, filtering)
        query = self._sort_users(filtering, query)
        query = self._paginate(filtering, query)

        organisation_users = self._connection.execute(query).fetchall()

        return [build_user_from_dict(user_dict) for user_dict in organisation_users]

    def get_total_organisation_users_count(self, organisation_pk: OrganisationPk, filtering: UserListFilter) -> int:
        query = self._get_organisation_users_query(organisation_pk, filtering).alias().count()

        result = self._connection.execute(query).fetchone()  # noqa: WPS110

        if result is None:
            return 0

        return result[0]

    def get_invitees(self, organisation_pk: OrganisationPk, filtering: InvitationListFilter) -> list[Invitation]:
        query = self._get_invitations_query(organisation_pk, filtering)
        query = self._paginate(filtering, query)
        email_dicts = self._connection.execute(query).fetchall()
        return [build_invitation_from_dict(email_dict) for email_dict in email_dicts]

    def get_total_invitees_count(self, organisation_pk: OrganisationPk, filtering: InvitationListFilter) -> int:
        query = self._get_invitations_query(organisation_pk, filtering)
        count = self._connection.execute(query.alias().count()).scalar()
        return count or 0

    def invite_user_to_organisation(
        self, inviter_pk: str, organisation_pk: OrganisationPk, invitation: Invitation
    ) -> Invitation:
        query = (
            insert(direct_invitation_table)
            .values(inviter_pk=inviter_pk, organisation_pk=organisation_pk, user_email=invitation.email)
            .returning(direct_invitation_table)
        )
        try:
            res = self._connection.execute(query).fetchone()
        except StatementError as err:
            if extract_database_error_type(err, self._database) == DatabaseErrorTypeEnum.UNIQUE_VIOLATION:
                raise InvitationAlreadyExistsError(
                    f"User with email {invitation.email} has already been invited to organisation {organisation_pk}."
                )

            raise IAMException(str(err))

        return build_invitation_from_dict(res)

    def delete_invitation(self, organisation_pk: OrganisationPk, user_email: str) -> None:
        query = (
            delete(direct_invitation_table)
            .where(direct_invitation_table.c.user_email == user_email)
            .where(direct_invitation_table.c.organisation_pk == organisation_pk)
        )

        answer = self._connection.execute(query)

        if answer.rowcount == 0:
            raise InvitationNotFoundError(
                f"User with email {user_email} is not invited to organisation {organisation_pk}."
            )

    def create_approval_request(self, organisation_pk: OrganisationPk, user_pk: str) -> ApprovalRequest:
        query = (
            insert(approval_request_table)
            .values(user_pk=user_pk, organisation_pk=organisation_pk)
            .returning(approval_request_table)
        )
        try:
            res = self._connection.execute(query).fetchone()
        except StatementError as err:
            if extract_database_error_type(err, self._database) == DatabaseErrorTypeEnum.UNIQUE_VIOLATION:
                raise ApprovalRequestAlreadyExistsError(
                    f"User with pk {user_pk} is already waiting for approval to join organisation with pk {organisation_pk}."
                )

            raise IAMException(str(err))

        return build_approval_request_from_dict(res)

    def get_total_approvals_count(self, organisation_pk: OrganisationPk, filtering: UserListFilter) -> int:
        joined_tables = join(user_table, approval_request_table)
        query = (
            select([approval_request_table.c.user_pk])
            .where(approval_request_table.c.organisation_pk == organisation_pk)
            .select_from(joined_tables)
        )
        query = self._filter_users(filtering, query)
        count = self._connection.execute(query.alias().count()).scalar()
        return count or 0

    def get_waiting_for_approvals(self, organisation_pk: OrganisationPk, filtering: UserListFilter) -> list[UserEntity]:
        joined_tables = join(user_table, approval_request_table)
        query = (
            select([user_table])
            .where(approval_request_table.c.organisation_pk == organisation_pk)
            .select_from(joined_tables)
        )
        query = self._filter_users(filtering, query)
        query = self._sort_users(filtering, query)
        query = self._paginate(filtering, query)
        users = self._connection.execute(query).fetchall()
        return [build_user_from_dict(u) for u in users]

    @staticmethod
    def _filter_organisations(filtering: OrganisationListFilter, query):
        if filtering.user_pk:
            query = query.where(
                organisation_table.c.pk.in_(
                    select([user_organisation_table.c.organisation_pk]).where(
                        user_organisation_table.c.user_pk == filtering.user_pk
                    )
                )
            )
        if filtering.organisation_type == OrganisationTypesEnum.PERSONAL:
            query = query.where(organisation_table.c.name.like(f"%{PERSONAL_ORGANISATION_POSTFIX}"))
        elif filtering.organisation_type == OrganisationTypesEnum.NON_PERSONAL:
            query = query.where(organisation_table.c.name.notlike(f"%{PERSONAL_ORGANISATION_POSTFIX}"))

        return query

    @staticmethod
    def _paginate(pagination: PaginationObject, query):
        if pagination.page and pagination.per_page:
            query = query.offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page)
        return query

    def _get_organisation_users_query(self, organisation_pk: OrganisationPk, filtering: UserListFilter):
        query = select([user_table]).where(
            user_table.c.pk.in_(
                select([user_organisation_table.c.user_pk]).where(
                    user_organisation_table.c.organisation_pk == organisation_pk
                )
            )
        )
        return self._filter_users(filtering, query)

    @staticmethod
    def _filter_users(filtering: UserListFilter, query):
        if filtering.full_name:
            full_name = functions.concat(user_table.c.first_name, user_table.c.last_name)
            query = query.where(full_name.ilike(f"%{filtering.full_name}%"))
        if filtering.pks:
            query = query.where(user_table.c.pk.in_(filtering.pks))
        return query

    @staticmethod
    def _sort_users(filtering: UserListFilter, query):
        if filtering.sort_field:
            if filtering.sort_field == UserSortingFieldsEnum.full_name_desc:
                query = query.order_by(desc(user_table.c.first_name)).order_by(
                    desc(user_table.c.last_name)
                )  # noqa: WPS221
            else:
                query = query.order_by(user_table.c.first_name).order_by(user_table.c.last_name)
        return query

    @staticmethod
    def _get_invitations_query(organisation_pk: OrganisationPk, filtering: InvitationListFilter):
        query = select([direct_invitation_table.c.user_email]).where(
            direct_invitation_table.c.organisation_pk == organisation_pk
        )
        if filtering.user_pk:
            query = query.where(direct_invitation_table.c.inviter_pk == filtering.user_pk)
        if filtering.sorting_field:
            if filtering.sorting_field == InvitationSortingFieldEnum.email_desc:
                query = query.order_by(desc(direct_invitation_table.c.user_email))
            else:
                query = query.order_by(asc(direct_invitation_table.c.user_email))
        if filtering.search_term:
            query = query.where(direct_invitation_table.c.user_email.ilike(f"%{filtering.search_term}%"))
        return query

    def delete_user_from_organisation(self, organisation_pk: OrganisationPk, user_pk: str) -> str:
        query = (
            delete(user_organisation_table)
            .where(user_organisation_table.c.user_pk == user_pk)
            .where(user_organisation_table.c.organisation_pk == organisation_pk)
            .returning(user_organisation_table.c.user_pk)
        )
        delete_query_result = self._connection.execute(query).fetchone()

        if not delete_query_result:
            raise UserOrganisationNotFoundError(f"There is no user {user_pk} in organisation {organisation_pk}.")

        return delete_query_result["user_pk"]

    def delete_approval_request(self, organisation_pk: OrganisationPk, user_pk: str) -> str:
        query = (
            delete(approval_request_table)
            .where(approval_request_table.c.user_pk == user_pk)
            .where(approval_request_table.c.organisation_pk == organisation_pk)
            .returning(approval_request_table.c.user_pk)
        )
        query_result = self._connection.execute(query).fetchone()

        if not query_result:
            raise ApprovalRequestNotFoundError(
                f"User {user_pk} has no approval request to join organisation {organisation_pk}"
            )

        return query_result["user_pk"]

    @property
    def _connection(self) -> Connection:
        return self._database.get_connection()
