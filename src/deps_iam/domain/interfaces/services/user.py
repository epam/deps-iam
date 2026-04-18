from abc import ABC, abstractmethod

from deps_iam.domain.dtos import ExpandedUser, UserListFilter, UserUpdateObject
from deps_iam.domain.entities.user import UserEntity


class IUserService(ABC):
    @abstractmethod
    def get(self, user_pk: str) -> UserEntity:
        ...

    @abstractmethod
    def get_expanded_user(self, user_pk: str) -> ExpandedUser:
        ...

    @abstractmethod
    def get_list(self, user_filter: UserListFilter = UserListFilter()) -> list[UserEntity]:
        ...

    @abstractmethod
    def add(self, user: UserEntity) -> UserEntity:
        ...

    @abstractmethod
    def update(self, user_pk: str, update_data: UserUpdateObject) -> UserEntity:
        ...

    @abstractmethod
    def upsert(self, user: UserEntity) -> None:
        ...

    @abstractmethod
    def delete(self, user_pk: str) -> None:
        ...

    @abstractmethod
    def get_api_key(self, user_pk: str) -> str:
        ...

    @abstractmethod
    def get_user_by_api_key(self, api_key: str) -> UserEntity:
        ...

    @abstractmethod
    def delete_api_key(self, user_pk: str) -> None:
        ...

    @abstractmethod
    def create_api_key(self, user_pk: str) -> str:
        ...

    @abstractmethod
    def get_user_by_email(self, email: str) -> UserEntity:
        ...
