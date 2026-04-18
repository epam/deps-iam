import abc

from ..group import GroupInfo
from .policy import Policy

__all__ = ["IPolicyRepository"]


class IPolicyRepository(abc.ABC):
    @abc.abstractmethod
    def all_policies_of_resource(self, resource: str) -> list[Policy]:
        pass

    @abc.abstractmethod
    def all_policies_of_resources(self, resources: list[str]) -> dict[str, list[Policy]]:
        pass

    @abc.abstractmethod
    def policy_of_id(self, policy_id: str) -> Policy:
        pass

    @abc.abstractmethod
    def save(self, resource: str, policy: Policy) -> None:
        pass

    @abc.abstractmethod
    def delete(self, policy: Policy) -> None:
        pass

    def delete_all(self, drns: list[str]) -> None:  # noqa: B027
        pass

    def save_all(self, policies: dict[str, Policy]) -> None:  # noqa: B027
        pass

    def save_user_policies(self, user_drn: str, group_info: GroupInfo) -> None:  # noqa: B027
        pass
