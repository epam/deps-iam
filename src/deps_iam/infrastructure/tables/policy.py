from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_iam.extras.datasource import metadata

__all__ = ["policy_table", "statement_table", "resource_has_policy_table"]
policy_table = Table(
    "policy",
    metadata,
    Column("id", String, primary_key=True),
)

statement_table = Table(
    "statement",
    metadata,
    Column("policy_id", String, ForeignKey("policy.id", ondelete="cascade", name="fk_policy_id"), nullable=False),
    Column("effect", String, nullable=False),
    Column("actions", JSONB, nullable=False),
    Column("resources", JSONB, nullable=False),
    Column("principals", JSONB, nullable=True),
)

resource_has_policy_table = Table(
    "resource_has_policy",
    metadata,
    Column("resource", String),
    Column("policy_id", String, ForeignKey("policy.id", ondelete="cascade", name="fk_policy_id"), nullable=False),
)
