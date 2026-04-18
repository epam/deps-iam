from typing import Any

from sqlalchemy import text

from deps_iam.infrastructure.tables import (
    policy_table,
    resource_has_policy_table,
    statement_table,
)


class PolicyQueryBuilder:
    def __init__(self):
        self.policy_table = policy_table
        self.statement_table = statement_table
        self.resource_has_policy_table = resource_has_policy_table
        self._sql_query = None

    def for_policy(self, *, where: Any = True) -> "PolicyQueryBuilder":
        self._sql_query = f"""
            SELECT {self.policy_table.c.id}, jsonb_agg(to_jsonb({self.statement_table}) - 'policy_id') as statements
            FROM {self.policy_table} LEFT JOIN statement
            ON {self.policy_table.c.id} = {self.statement_table.c.policy_id}
            WHERE {where}
            GROUP BY {self.policy_table.c.id}
        """
        return self

    def for_resources(self, *, where: Any = True) -> "PolicyQueryBuilder":
        self._sql_query = f"""
        WITH policy_statements AS ({self._sql_query}),
        resource_policy as
        (
            SELECT {self.resource_has_policy_table.c.resource}, jsonb_agg(to_jsonb(policy_statements)) as policies
            FROM {self.resource_has_policy_table}
            LEFT JOIN policy_statements
            ON {self.resource_has_policy_table.c.policy_id} = policy_statements.id
            WHERE {where}
            GROUP BY {self.resource_has_policy_table.c.resource}
        )
        SELECT * from resource_policy;
        """
        return self

    def build(self):
        return text(self._sql_query)
