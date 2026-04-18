from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint

from deps_iam.extras.datasource import metadata

direct_invitation_table = Table(
    "direct_invitation",
    metadata,
    Column("pk", Integer, primary_key=True, autoincrement=True),
    Column(
        "inviter_pk",
        String,
        ForeignKey("user.pk", ondelete="cascade", name="inviter_pk_fkey"),
        nullable=False,
    ),
    Column(
        "organisation_pk",
        String,
        ForeignKey("organisation.pk", ondelete="cascade", name="organisation_pk_fkey"),
        nullable=False,
    ),
    Column(
        "user_email",
        String,
        nullable=False,
    ),
    UniqueConstraint("organisation_pk", "user_email", name="unique_organisation_invitation"),
)
