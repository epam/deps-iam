from sqlalchemy import Column, String, Table

from deps_iam.extras.datasource import metadata

permission_table = Table(
    "permission",
    metadata,
    Column("name", String(32), nullable=False),  # noqa: WPS432
)
