from typing import List

from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

from deps_iam.domain.entities.permission import PermissionEntity
from deps_iam.domain.exceptions import (
    PermissionAlreadyExistsError,
    PermissionNotFoundError,
)
from deps_iam.domain.interfaces.repositories import IPermissionRepository
from deps_iam.extras.datasource import Database
from deps_iam.infrastructure.tables.permission import permission_table

from .mappers import build_permission_entity


class PermissionRepository(IPermissionRepository):
    def __init__(self, database: Database):
        self._database = database

    def get_list(self) -> List[PermissionEntity]:
        query = select([permission_table])

        permissions = self._connection.execute(query)

        return [build_permission_entity(permission_entity) for permission_entity in permissions]

    def add(self, permission_entity: PermissionEntity) -> PermissionEntity:
        query = insert(permission_table).values(name=permission_entity.name).returning(permission_table)

        try:
            permission_obj = self._connection.execute(query).fetchone()
        except IntegrityError:
            raise PermissionAlreadyExistsError(f"Permission `{permission_entity.name}` already exists.")

        return build_permission_entity(permission_obj)

    def delete(self, permission_entity: PermissionEntity) -> None:
        query = (
            delete(permission_table)
            .where(permission_table.c.name == permission_entity.name)
            .returning(permission_table)
        )

        delete_id = self._connection.execute(query).fetchone()
        if delete_id is None:
            raise PermissionNotFoundError(f"Permission'{permission_entity.name}' doesn't exist.")

    @property
    def _connection(self) -> Connection:
        return self._database.get_connection()
