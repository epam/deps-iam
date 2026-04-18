from sqlalchemy import Text, delete, insert, text
from sqlalchemy.sql import Delete, Insert

from deps_iam.infrastructure.tables import (
    policy_table,
    resource_has_policy_table,
    statement_table,
)

from .query_builder import PolicyQueryBuilder


class PolicyQueryFactory:
    def __init__(self):
        self._policy_table = policy_table
        self._statement_table = statement_table
        self._resource_has_policy_table = resource_has_policy_table

    def all_policies_of_resource_query(self) -> Text:
        resource_matches = f"{self._resource_has_policy_table.c.resource} = :resource"
        return PolicyQueryBuilder().for_policy().for_resources(where=resource_matches).build()

    def policy_of_id(self) -> Text:
        policy_matches = f"{self._policy_table.c.id} = :policy_id"
        return PolicyQueryBuilder().for_policy(where=policy_matches).build()

    def all_policies_of_resources(self) -> Text:
        resource_in_resources = f"{self._resource_has_policy_table.c.resource} IN :resources"
        return PolicyQueryBuilder().for_policy().for_resources(where=resource_in_resources).build()

    def delete_policy(self) -> Delete:
        where = text(f"{self._policy_table.c.id} = :policy_id")
        return delete(self._policy_table).where(where)

    def insert_policy(self) -> Insert:
        return insert(self._policy_table)

    def insert_statements(self) -> Insert:
        return insert(self._statement_table)

    def insert_resource_has_policy(self) -> Insert:
        return insert(self._resource_has_policy_table)
