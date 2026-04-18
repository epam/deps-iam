from abc import ABC, abstractmethod

from .group import Group

__all__ = ["IGroupRepository"]


class IGroupRepository(ABC):
    @abstractmethod
    def save(self, group: Group) -> None:
        pass

    @abstractmethod
    def delete(self, group_id: str) -> None:
        pass

    def group_of_id(self, group_id: str) -> Group:  # noqa: B027
        pass
