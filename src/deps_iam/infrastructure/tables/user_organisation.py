from sqlalchemy import Column, ForeignKey, String, Table

from deps_iam.extras.datasource import metadata

user_organisation_table = Table(
    "user_organisation",
    metadata,
    Column("user_pk", String, ForeignKey("user.pk", ondelete="cascade"), nullable=False, primary_key=True),
    Column(
        "organisation_pk", String, ForeignKey("organisation.pk", ondelete="cascade"), nullable=False, primary_key=True
    ),
)
