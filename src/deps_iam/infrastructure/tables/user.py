from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    UniqueConstraint,
    func,
)

from deps_iam.extras.datasource import metadata

user_table = Table(
    "user",
    metadata,
    Column("pk", String, primary_key=True),
    Column("created_at", DateTime(timezone=True), default=datetime.utcnow, server_default=func.now()),
    Column("username", String, nullable=True),
    Column("email", String, nullable=False),
    Column("first_name", String),
    Column("last_name", String),
    Column(
        "organisation",
        String,
        ForeignKey("organisation.pk", ondelete="set null", name="organisation_pk_fkey"),
        nullable=True,
    ),
    UniqueConstraint("email", name="unique_user_email"),
)
