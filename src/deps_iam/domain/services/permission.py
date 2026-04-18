from typing import List

from deps_iam.domain.entities.permission import PermissionEntity
from deps_iam.infrastructure.uow import UnitOfWork


class PermissionService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def get_list(self) -> List[PermissionEntity]:
        with self._uow:
            return self._uow.permission.get_list()

    def add(self, permission_entity: PermissionEntity) -> PermissionEntity:
        with self._uow:
            res = self._uow.permission.add(permission_entity)
            self._uow.commit()

        return res

    def delete(self, permission_entity: PermissionEntity) -> None:
        with self._uow:
            res = self._uow.permission.delete(permission_entity)
            self._uow.commit()

        return res
