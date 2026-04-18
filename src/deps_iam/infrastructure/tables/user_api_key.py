from sqlalchemy import Column, ForeignKey, String, Table, UniqueConstraint

from deps_iam.extras.datasource import metadata

user_api_key_table = Table(
    "user_api_key",
    metadata,
    Column("user_pk", String, nullable=False),
    UniqueConstraint("user_pk", name="user_pk_uckey"),
    Column(
        "api_key",
        String,
        ForeignKey("user.pk", ondelete="cascade", name="user_api_key_fkey"),
        nullable=False,
    ),
)
