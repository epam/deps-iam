from typing import Any

from sqlalchemy.engine import RowProxy

from deps_iam.domain.entities import PermissionEntity, RoleEntity


def build_add_role_dict(entity: RoleEntity, organisation: str) -> dict[str, Any]:
    """RoleEntity -> dict"""
    return {
        "name": entity.name,
        "organisation": organisation,
    }


def build_update_role_dict(entity: RoleEntity) -> dict[str, Any]:
    """RoleEntity -> dict"""
    return {"name": entity.name}


def build_role_entity(role_row: RowProxy) -> RoleEntity:
    """dict -> RoleEntity"""
    permissions = [PermissionEntity(name=name) for name in role_row.permissions if name]
    return RoleEntity(
        pk=role_row["pk"],
        name=role_row["name"],
        permissions=permissions,
    )
