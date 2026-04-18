from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint

from deps_iam.extras.datasource import metadata

role_table = Table(
    "role",
    metadata,
    Column("pk", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column(
        "organisation",
        String,
        ForeignKey("organisation.pk", ondelete="cascade", name="organisation_pk_fkey"),
        nullable=False,
    ),
    UniqueConstraint("name", "organisation", name="role_name_organisation_uckey"),
)
