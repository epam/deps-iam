from dataclasses import dataclass, field
from typing import NewType, Optional

from deps_iam.domain.entities import PermissionEntity

RolePk = NewType("RolePk", int)


@dataclass
class RoleEntity:
    pk: Optional[RolePk]
    name: str
    permissions: list[PermissionEntity] = field(default_factory=list)
