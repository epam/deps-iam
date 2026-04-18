from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint

from deps_iam.extras.datasource import metadata

role_has_permission_table = Table(
    "role_has_permission",
    metadata,
    Column(
        "role_pk",
        Integer,
        ForeignKey("role.pk", ondelete="cascade", name="role_pk_fkey"),
        nullable=False,
    ),
    Column(
        "permission_name",
        String,
        ForeignKey("permission.name", ondelete="cascade", name="permission_name_fkey"),
        nullable=False,
    ),
    UniqueConstraint("role_pk", "permission_name", name="role_pk_permission_name_uckey"),
)
