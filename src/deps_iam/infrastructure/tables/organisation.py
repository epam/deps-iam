import uuid

from sqlalchemy import Column, String, Table

from deps_iam.extras.datasource import metadata

organisation_table = Table(
    "organisation",
    metadata,
    Column("pk", String, primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("name", String, nullable=False),
    Column("customization_url", String),
)
