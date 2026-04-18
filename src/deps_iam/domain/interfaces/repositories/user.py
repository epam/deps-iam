from abc import ABC, abstractmethod

from deps_iam.domain.dtos import ExpandedUser, UserListFilter, UserUpdateObject
from deps_iam.domain.entities.user import UserEntity


class IUserRepository(ABC):
    @abstractmethod
    def get(self, pk: str) -> UserEntity:
        pass

    @abstractmethod
    def get_expanded_user(self, pk: str) -> ExpandedUser:
        pass

    @abstractmethod
    def get_list(self, user_filter: UserListFilter) -> list[UserEntity]:
        pass

    @abstractmethod
    def add(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def update(self, user_pk: str, update_data: UserUpdateObject) -> UserEntity:
        pass

    @abstractmethod
    def upsert(self, user: UserEntity) -> None:
        pass

    @abstractmethod
    def delete(self, user_pk: str) -> None:
        pass

    @abstractmethod
    def deactivate_user_organisation(self, user_pk: str) -> UserEntity:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> UserEntity:
        pass
