from typing import Optional

from sqlalchemy import delete, func, insert, join, or_, select, update
from sqlalchemy.engine import Connection, RowProxy
from sqlalchemy.exc import StatementError

from deps_iam.domain.entities import RoleEntity, RolePk
from deps_iam.domain.exceptions import (
    OrganisationNotFoundError,
    PermissionNotFoundError,
    RoleAlreadyExistsError,
    RoleNotFoundError,
)
from deps_iam.domain.interfaces.repositories import IRoleRepository
from deps_iam.extras.datasource import Database
from deps_iam.infrastructure.repositories.constants import DatabaseErrorTypeEnum
from deps_iam.infrastructure.repositories.error_extractor import (
    extract_database_error_type,
)
from deps_iam.infrastructure.tables import (
    permission_table,
    role_has_permission_table,
    role_table,
)

from .mappers import build_add_role_dict, build_role_entity, build_update_role_dict


class RoleRepository(IRoleRepository):
    def __init__(self, database: Database, default_organisation: str) -> None:
        self._database = database
        self._default_organisation = default_organisation

    @property
    def select_role(self):
        joined_tables = join(role_table, role_has_permission_table, isouter=True)
        joined_tables = join(joined_tables, permission_table, isouter=True)

        return (
            select(
                [
                    role_table.c.pk,
                    role_table.c.name,
                    func.array_agg(permission_table.c.name).label("permissions"),
                ]
            )
            .select_from(joined_tables)
            .group_by(role_table.c.pk)
        )

    def create(self, entity: RoleEntity, organisation: Optional[str] = None) -> RoleEntity:
        organisation = organisation or self._default_organisation

        role_row = self._add_role(entity, organisation)
        role_pk = role_row["pk"]
        if entity.permissions:
            self._add_permissions(role_pk, entity)

        return self.get(role_pk)

    def get(self, pk: RolePk) -> RoleEntity:
        query = self.select_role.where(
            or_(role_has_permission_table.c.role_pk == pk, role_table.c.pk == pk),
        )
        res = self._connection.execute(query).fetchone()

        if not res:
            raise RoleNotFoundError(f"Role with pk '{pk}' doesn't exist")

        return build_role_entity(res)

    def delete(self, pk: RolePk) -> None:
        delete_query = delete(role_table).where(role_table.c.pk == pk)
        res = self._connection.execute(delete_query)

        if not res.rowcount:
            raise RoleNotFoundError(f"Role with pk '{pk}' doesn't exist")

    def update(self, pk: RolePk, entity: RoleEntity) -> RoleEntity:
        role_dict = build_update_role_dict(entity=entity)
        update_query = (
            update(role_table)
            .values(**role_dict)
            .where(
                role_table.c.pk == pk,
            )
            .returning(role_table.c.pk)
        )

        try:
            res = self._connection.execute(update_query).fetchone()
        except StatementError as err:
            if extract_database_error_type(err, self._database) == DatabaseErrorTypeEnum.UNIQUE_VIOLATION:
                raise RoleAlreadyExistsError(f"Role '{entity.name}' already exists")

            raise

        if not res:
            raise RoleNotFoundError(f"Role with pk '{pk}' doesn't exist")

        self._delete_permissions(pk)
        if entity.permissions:
            self._add_permissions(pk, entity)

        return self.get(pk)

    def get_list(self) -> list[RoleEntity]:
        query = self.select_role

        role_rows = self._connection.execute(query).fetchall()

        return [build_role_entity(role) for role in role_rows]

    @property
    def _connection(self) -> Connection:
        return self._database.get_connection()

    def _add_role(self, entity: RoleEntity, organisation: str) -> RowProxy:
        role_dict = build_add_role_dict(entity, organisation)
        query = insert(role_table).values(**role_dict).returning(role_table.c.pk)

        try:
            res = self._connection.execute(query).fetchone()

        except StatementError as err:
            db_error = extract_database_error_type(err, self._database)

            if db_error == DatabaseErrorTypeEnum.UNIQUE_VIOLATION:
                role_name = role_dict["name"]
                raise RoleAlreadyExistsError(f"Role '{role_name}' already exists")

            elif db_error == DatabaseErrorTypeEnum.FOREIGN_KEY_VIOLATION:
                raise OrganisationNotFoundError(f'{organisation} is not present in table "organisation"')

            raise

        return res

    def _add_permissions(self, role_pk: int, entity: RoleEntity) -> None:
        permission_list = [(role_pk, permission.name) for permission in entity.permissions]
        insert_query = insert(role_has_permission_table).values(permission_list)
        try:
            self._connection.execute(insert_query)
        except StatementError as err:
            if extract_database_error_type(err, self._database) == DatabaseErrorTypeEnum.FOREIGN_KEY_VIOLATION:
                raise PermissionNotFoundError(str(err))

            raise

    def _delete_permissions(self, role_pk: int) -> None:
        self._connection.execute(
            delete(role_has_permission_table).where(role_has_permission_table.c.role_pk == role_pk)
        )
