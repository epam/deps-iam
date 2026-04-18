from collections import defaultdict

from deps_iam.domain.model import GroupInfo, IPolicyRepository, Policy


class FakePolicyRepository(IPolicyRepository):
    def __init__(self):
        self._policy_db: dict[str, Policy] = {}
        self._mapping_db = defaultdict(list)

    def all_policies_of_resource(self, resource: str) -> list[Policy]:
        return [self._policy_db[policy_id] for policy_id in self._mapping_db[resource]]

    def all_policies_of_resources(self, resources: list[str]) -> dict[str, list[Policy]]:
        pass

    def policy_of_id(self, policy_id: str) -> Policy:
        pass

    def save(self, resource: str, policy: Policy) -> None:
        pass

    def delete(self, policy: Policy) -> None:
        pass

    def save_all(self, policies: dict[str, Policy]) -> None:
        for drn, policy in policies.items():
            self._policy_db[policy.id()] = policy
            self._mapping_db[drn].append(policy.id())

    def save_user_policies(self, user_drn: str, group_info: GroupInfo) -> None:
        group_policy_ids = self._mapping_db[group_info.group_drn]
        role_policy_ids = self._mapping_db[group_info.role_drn]
        self._mapping_db[user_drn].extend(group_policy_ids + role_policy_ids)

    def delete_all(self, drns: list[str]) -> None:
        for drn in drns:
            policy_ids = self._mapping_db.pop(drn, [])
            for id_ in policy_ids:
                self._policy_db.pop(id_, None)
