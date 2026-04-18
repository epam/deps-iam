from abc import ABC, abstractmethod
from typing import Optional

from deps_iam.domain.entities import RoleEntity, RolePk


class IRoleRepository(ABC):
    @abstractmethod
    def create(self, entity: RoleEntity, organisation: Optional[str] = None) -> RoleEntity:
        pass

    @abstractmethod
    def get(self, pk: RolePk) -> RoleEntity:
        pass

    @abstractmethod
    def delete(self, pk: RolePk) -> None:
        pass

    @abstractmethod
    def update(self, pk: RolePk, entity: RoleEntity) -> RoleEntity:
        pass

    @abstractmethod
    def get_list(self) -> list[RoleEntity]:
        pass
