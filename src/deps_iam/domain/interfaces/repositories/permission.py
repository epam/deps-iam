from abc import ABC, abstractmethod
from typing import List

from deps_iam.domain.entities.permission import PermissionEntity


class IPermissionRepository(ABC):
    @abstractmethod
    def get_list(self) -> List[PermissionEntity]:
        pass

    @abstractmethod
    def add(self, permission_entity: PermissionEntity) -> PermissionEntity:
        pass

    @abstractmethod
    def delete(self, permission_entity: PermissionEntity) -> None:
        pass
