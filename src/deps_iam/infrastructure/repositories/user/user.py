from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection
from sqlalchemy.exc import StatementError
from sqlalchemy.sql import Select, null, select

from deps_iam.domain.dtos import ExpandedUser, UserListFilter, UserUpdateObject
from deps_iam.domain.entities.user import UserEntity
from deps_iam.domain.exceptions import (
    IAMException,
    OrganisationNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from deps_iam.domain.interfaces.repositories.user import IUserRepository
from deps_iam.extras.datasource import Database
from deps_iam.infrastructure.repositories.constants import DatabaseErrorTypeEnum
from deps_iam.infrastructure.repositories.error_extractor import (
    extract_database_error_type,
)
from deps_iam.infrastructure.tables.organisation import organisation_table
from deps_iam.infrastructure.tables.user import user_table

from .mappers import (
    build_dict_from_user,
    build_dict_from_user_update_object,
    build_expanded_user_from_dict,
    build_user_from_dict,
)


class UserRepository(IUserRepository):
    def __init__(self, database: Database):
        self._database = database

    def get(self, pk: str) -> UserEntity:
        query = self._get_query_with_uuid(pk)

        get_query_result = self._connection.execute(query).fetchone()

        if not get_query_result:
            raise UserNotFoundError
        return build_user_from_dict(get_query_result)

    def get_expanded_user(self, pk: str) -> ExpandedUser:
        query = (
            select(
                [
                    user_table,
                    organisation_table.c.pk.label("org_pk"),
                    organisation_table.c.name.label("org_name"),
                    organisation_table.c.customization_url.label("org_customization_url"),
                ]
            )
            .select_from(user_table.outerjoin(organisation_table))
            .where(user_table.c.pk == pk)
        )

        res = self._connection.execute(query).fetchone()

        if not res:
            raise UserNotFoundError

        return build_expanded_user_from_dict(res)

    def get_list(self, user_filter: UserListFilter = UserListFilter()) -> list[UserEntity]:
        query = self._filter(user_filter)
        get_query_result = self._connection.execute(query).fetchall()

        return [build_user_from_dict(user_dict) for user_dict in get_query_result]

    def add(self, user: UserEntity) -> UserEntity:
        query = self.insert_query.values(**build_dict_from_user(user)).returning(user_table)

        try:
            create_query_result = self._connection.execute(query).fetchone()
        except StatementError as err:
            if extract_database_error_type(err, self._database) == DatabaseErrorTypeEnum.UNIQUE_VIOLATION:
                raise UserAlreadyExistsError(f"User `{user.pk}` already exists.")
            raise IAMException(str(err))

        return build_user_from_dict(create_query_result)

    def update(self, user_pk: str, update_data: UserUpdateObject) -> UserEntity:
        update_dict = build_dict_from_user_update_object(update_data)
        query = self._update_query_with_uuid(user_pk).values(**update_dict).returning(user_table)  # noqa: WPS221
        try:
            update_query_result = self._connection.execute(query).fetchone()
        except StatementError as err:
            if extract_database_error_type(err, self._database) == DatabaseErrorTypeEnum.FOREIGN_KEY_VIOLATION:
                raise OrganisationNotFoundError(
                    f"Can't update user {user_pk} with organisation {update_data.organisation}."
                )

            raise IAMException(str(err))

        if not update_query_result:
            raise UserNotFoundError(f"User `{user_pk}` not found.")

        return build_user_from_dict(update_query_result)

    def upsert(self, user: UserEntity) -> None:
        update_dict = build_dict_from_user_update_object(UserUpdateObject.from_entity(user))

        self._connection.execute(
            insert(user_table)
            .values(**build_dict_from_user(user))
            .on_conflict_do_update(index_elements=["pk"], set_=update_dict)
        )

    def delete(self, user_pk: str) -> None:
        query = user_table.delete().where(user_table.c.pk == user_pk).returning(user_table.c.pk)  # noqa: WPS221
        delete_query_result = self._connection.execute(query).fetchone()

        if not delete_query_result:
            raise UserNotFoundError(f"User `{user_pk}` not found.")

    def deactivate_user_organisation(self, user_pk: str) -> UserEntity:
        query = self._update_query_with_uuid(user_pk).values(organisation=null()).returning(user_table)
        update_query_result = self._connection.execute(query).fetchone()

        if not update_query_result:
            raise UserNotFoundError(f"User `{user_pk}` not found.")

        return build_user_from_dict(update_query_result)

    def get_user_by_email(self, email: str) -> UserEntity:
        query = self.get_query.where(user_table.c.email == email)

        get_query_result = self._connection.execute(query).fetchone()

        if not get_query_result:
            raise UserNotFoundError
        return build_user_from_dict(get_query_result)

    @property
    def get_query(self):
        return user_table.select()

    @property
    def insert_query(self):
        return user_table.insert()

    @property
    def update_query(self):
        return user_table.update()

    @property
    def _connection(self) -> Connection:
        return self._database.get_connection()

    def _get_query_with_uuid(self, pk: str):
        return self.get_query.where(user_table.c.pk == pk)

    def _update_query_with_uuid(self, pk: str):
        return self.update_query.where(user_table.c.pk == pk)

    def _filter(self, filtering: UserListFilter) -> Select:
        query = self.get_query
        if filtering.pks:
            query = query.where(user_table.c.pk.in_(filtering.pks))
        if filtering.created_at:
            if filtering.created_at.start:
                query = query.where(user_table.c.created_at >= filtering.created_at.start)
            if filtering.created_at.end:
                query = query.where(user_table.c.created_at <= filtering.created_at.end)
        if filtering.username is not None:
            query = query.where(user_table.c.username.like(f"%{filtering.username}%"))
        if filtering.email is not None:
            query = query.where(user_table.c.email == filtering.email)
        if filtering.first_name is not None:
            query = query.where(user_table.c.first_name.like(f"%{filtering.first_name}%"))
        if filtering.last_name is not None:
            query = query.where(user_table.c.last_name.like(f"%{filtering.last_name}%"))
        if filtering.emails is not None:
            query = query.where(user_table.c.email.in_(filtering.emails))

        return query
