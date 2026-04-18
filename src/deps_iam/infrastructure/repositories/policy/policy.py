from typing import Iterable

from deps_iam.domain.exceptions.policy import PolicyNotFoundError
from deps_iam.domain.model import IPolicyRepository, Policy
from deps_iam.extras.datasource import Database

from .mappers import PolicyListMapper, PolicyMapper, ResourcePolicyMapper
from .query_factory import PolicyQueryFactory


class PolicyRepository(IPolicyRepository):
    def __init__(self, database: Database) -> None:
        self._database = database
        self._qf = PolicyQueryFactory()

    def all_policies_of_resource(self, resource: str) -> Iterable[Policy]:
        query = self._qf.all_policies_of_resource_query()
        with self._database.connection() as conn:
            res = conn.execute(query, resource=resource).fetchone()
        if not res:
            return []
        return PolicyListMapper.from_dict(res["policies"])

    def all_policies_of_resources(self, resources: list[str]) -> dict[str, list[Policy]]:
        query = self._qf.all_policies_of_resources()
        with self._database.connection() as conn:
            res = conn.execute(query, resources=tuple(resources)).fetchall()
        return ResourcePolicyMapper.from_dict(res)

    def policy_of_id(self, policy_id: str) -> Policy:
        query = self._qf.policy_of_id()
        with self._database.connection() as conn:
            res = conn.execute(query, policy_id=policy_id).fetchone()
            if not res:
                raise PolicyNotFoundError(policy_id)
        return PolicyMapper.from_dict(res)

    def save(self, resource: str, policy: Policy) -> None:
        policy_dict = PolicyMapper.to_dict(policy)
        statements_dict = policy_dict["statements"]
        policy_id = policy.id()
        with self._database.connection() as conn:
            conn.execute(self._qf.delete_policy(), policy_id=policy_id)
            conn.execute(self._qf.insert_policy().values(id=policy_id))
            conn.execute(
                self._qf.insert_statements().values(
                    [{"policy_id": policy_id, **statement} for statement in statements_dict]
                )
            )
            conn.execute(self._qf.insert_resource_has_policy().values(resource=resource, policy_id=policy_id))

    def delete(self, policy: Policy) -> None:
        with self._database.connection() as conn:
            conn.execute(self._qf.delete_policy(), policy_id=policy.id())
