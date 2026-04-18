from deps_iam.domain.model import Group, IPolicyRepository, User

__all__ = ["PolicyService"]


class PolicyService:
    def __init__(self, policy_repository: IPolicyRepository) -> None:
        self._policy_repository = policy_repository

    def save_group_policies(self, group: Group) -> None:
        policies = group.make_policies()
        self._policy_repository.save_all(policies)

    def delete_policies(self, drns: list[str]) -> None:
        self._policy_repository.delete_all(drns)

    def save_user_policies(self, user: User) -> None:
        self._policy_repository.save_user_policies(user.drn, user.active_group)
