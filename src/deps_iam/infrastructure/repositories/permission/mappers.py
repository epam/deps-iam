from sqlalchemy.engine import RowProxy

from deps_iam.domain.entities.permission import PermissionEntity


def build_permission_entity(permission_obj: RowProxy) -> PermissionEntity:
    return PermissionEntity(name=permission_obj["name"])
