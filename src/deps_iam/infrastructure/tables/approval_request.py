from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
    func,
)

from deps_iam.extras.datasource import metadata

from .user import user_table

approval_request_table = Table(
    "approval_request",
    metadata,
    Column("pk", Integer, primary_key=True, autoincrement=True),
    Column(
        "user_pk",
        String,
        ForeignKey(user_table.c.pk, ondelete="cascade", name="user_pk_fkey"),
        nullable=False,
    ),
    Column(
        "organisation_pk",
        String,
        ForeignKey("organisation.pk", ondelete="cascade", name="organisation_pk_fkey"),
        nullable=False,
    ),
    Column("created_at", DateTime(timezone=True), default=datetime.utcnow, server_default=func.now()),
    UniqueConstraint("user_pk", "organisation_pk", name="unique_user_approval"),
)
