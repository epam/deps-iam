from abc import ABC, abstractmethod


class IUserApiKeyRepository(ABC):
    @abstractmethod
    def create(self, user_pk: str, api_key: str) -> str:
        ...

    @abstractmethod
    def get(self, user_pk: str) -> str:
        ...

    @abstractmethod
    def delete(self, user_pk: str) -> None:
        ...

    @abstractmethod
    def get_user_by_api_key(self, api_key: str) -> str:
        ...
