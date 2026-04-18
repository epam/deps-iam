from abc import ABC, abstractmethod

from ..shared import EntityId
from .user import User

__all__ = ["IUserRepository"]


class IUserRepository(ABC):
    @abstractmethod
    def user_of_id(self, id_: EntityId) -> User:
        pass

    @abstractmethod
    def has_user_with_id(self, id_: EntityId) -> bool:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def delete(self, user_id: str) -> None:
        pass
