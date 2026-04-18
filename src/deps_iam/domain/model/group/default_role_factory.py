from ..policy import Action, DocumentTypeAction, Policy, Resource, StatementBuilder
from ..shared import EntityId, EntityName
from .role import Role
from .role_type import RoleType

__all__ = ["DefaultRoleFactory"]


class DefaultRoleFactory:
    def __init__(self, tenant_id: EntityId, group_id: EntityId, group_drn: str) -> None:
        self._tenant_id = tenant_id
        self._group_id = group_id
        self._group_drn = group_drn

    def make_owner(self) -> Role:
        return Role(
            group_id=self._group_id,
            name=self._create_name(name=RoleType.OWNER, group_drn=self._group_drn),
            policy=self._make_owner_policy(),
        )

    def make_user(self):
        return Role(
            group_id=self._group_id,
            name=self._create_name(name=RoleType.USER, group_drn=self._group_drn),
            policy=self._make_user_policy(),
        )

    def _make_owner_policy(self) -> Policy:
        return Policy(
            id_=EntityId(),
            statements=[
                StatementBuilder()
                .for_resources([Resource(f"drn:*:{self._tenant_id()}:{self._group_id()}/*")])
                .allow_all_actions()
                .build()
            ],
        )

    def _make_user_policy(self) -> Policy:
        return Policy(
            id_=EntityId(),
            statements=[
                StatementBuilder()
                .for_resources([Resource(f"drn:document_type:{self._tenant_id()}:{self._group_id()}/*")])
                .allow_actions([Action(DocumentTypeAction.ADD_TYPE)])
                .build()
            ],
        )

    @classmethod
    def _create_name(cls, name: str, group_drn: str) -> EntityName:
        return EntityName(name=name, drn=f"{group_drn}/role/{name}")
