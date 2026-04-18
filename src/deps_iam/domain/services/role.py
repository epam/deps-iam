from deps_iam.domain.entities import RoleEntity, RolePk
from deps_iam.infrastructure.uow import UnitOfWork


class RoleService:
    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    def create(self, entity: RoleEntity) -> RoleEntity:
        with self._uow:
            res = self._uow.role.create(entity)
            self._uow.commit()

        return res

    def get(self, pk: RolePk) -> RoleEntity:
        with self._uow:
            return self._uow.role.get(pk)

    def update(self, pk: RolePk, entity: RoleEntity) -> RoleEntity:
        with self._uow:
            res = self._uow.role.update(pk, entity)
            self._uow.commit()

        return res

    def delete(self, pk: RolePk) -> None:
        with self._uow:
            self._uow.role.delete(pk)
            self._uow.commit()

    def get_list(self) -> list[RoleEntity]:
        with self._uow:
            return self._uow.role.get_list()
