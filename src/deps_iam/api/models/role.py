from pydantic import BaseModel, ConfigDict, Field

from deps_iam.domain.entities import PermissionEntity, RoleEntity, RolePk


class PermissionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str

    def to_domain(self):
        return PermissionEntity(name=self.name)


class RoleModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pk: RolePk
    name: str
    permissions: list[PermissionModel] = Field(default_factory=list)

    def to_domain(self):
        return RoleEntity(
            pk=self.pk,
            name=self.name,
            permissions=[permission_model.to_domain() for permission_model in self.permissions],
        )


class RoleAddModel(RoleModel):
    pk: RolePk | None = None
