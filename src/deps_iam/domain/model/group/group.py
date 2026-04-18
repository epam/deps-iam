from typing import Optional, Type

from ...exceptions import RoleNotFoundError, UserNotFoundError
from ..policy import Action, Policy, Resource, StatementBuilder
from ..shared import EntityId, EntityName, UserInfo
from ..shared.guards import Guard, ImmutableCheck
from .default_role_factory import DefaultRoleFactory
from .group_info import GroupInfo
from .invitation import Invitation
from .role import Role
from .role_type import RoleType

__all__ = ["Group"]


class Group:
    id = Guard[EntityId](EntityId, ImmutableCheck())
    tenant_id = Guard[EntityId](EntityId, ImmutableCheck())
    name = Guard[EntityName](EntityName)
    users = Guard[list[EntityId]](list, ImmutableCheck())
    invitations = Guard[list[Invitation]](list, ImmutableCheck())
    approval_requests = Guard[list[UserInfo]](list, ImmutableCheck())
    roles = Guard[dict[RoleType, Role]](dict, ImmutableCheck())

    def __init__(
        self,
        id_: EntityId,
        tenant_id: EntityId,
        name: str,
        users: Optional[list[EntityId]] = None,
        invitations: Optional[list[Invitation]] = None,
        approval_requests: Optional[list[UserInfo]] = None,
        roles: Optional[list[Role]] = None,
    ):
        self.id = id_
        self.tenant_id = tenant_id
        self.name = self._create_name(name)
        self.users = users or []
        self.invitations = invitations or []
        self.approval_requests = approval_requests or []

        self._default_role_factory = DefaultRoleFactory(
            tenant_id=self.tenant_id,
            group_id=self.id,
            group_drn=self.name.drn,
        )
        self.roles = {role.name.name: role for role in roles} if roles else self._initiate_roles()
        self._user_role_mapping: dict[str, Role] = {}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    def __str__(self) -> str:
        return f"<Group> id: {self.id}, name: {self.name}"

    @property
    def group_policy_factory(self) -> Type["_PolicyFactory"]:
        return self._PolicyFactory

    @property
    def drn(self) -> str:
        return self.name.drn

    def accept(self, user_id: EntityId) -> None:
        if not self._is_group_has_user(user_id):
            self.users.append(user_id)
            self._user_role_mapping[user_id()] = self.roles[RoleType.USER]

    def create_invitations(self, invitations: list[str]) -> None:
        pass

    def remove_invitation(self, user_id: EntityId) -> None:
        pass

    def approve(self, user_id: EntityId) -> None:
        pass

    def decline(self, user_id: EntityId) -> None:
        pass

    def give_ownership(self, user_id: EntityId) -> None:
        if self._is_group_has_user(user_id):
            self._user_role_mapping[user_id()] = self.roles[RoleType.OWNER]
            return
        raise UserNotFoundError(f"User {user_id} is not in group {self.id.value}")

    def _create_name(self, name: str) -> EntityName:
        return EntityName(name=name, drn=f"drn:iam:{self.tenant_id()}:group/{self.id()}")  # noqa: WPS221

    def role_of_user(self, user_id: str) -> Role:
        if (user_role := self._user_role_mapping.get(user_id)) is None:
            raise RoleNotFoundError(f"Role for user {user_id} not found")
        return user_role

    def make_group_info(self, user_id: str) -> GroupInfo:
        return GroupInfo(
            group=self.name,
            role=self.role_of_user(user_id).name,
        )

    def make_policies(self) -> dict[str, Policy]:
        policies = {self.name.drn: self._make_policy()}
        for role in self.roles.values():
            policies[role.drn] = role.policy

        return policies

    def join(self, user_info: UserInfo) -> None:
        if self._is_group_has_user(user_info.id):
            return
        elif self._is_user_invited(user_info.id):
            self.accept(user_info.id)
            self.remove_invitation(user_info.id)
            return
        self.add_approval_request(user_info)

    def add_approval_request(self, user_info: UserInfo) -> None:
        if user_info not in self.approval_requests:
            self.approval_requests.append(user_info)

    def _initiate_roles(self):
        return {
            RoleType.OWNER: self._default_role_factory.make_owner(),
            RoleType.USER: self._default_role_factory.make_user(),
        }

    def _make_policy(self) -> Policy:
        return self.group_policy_factory.make_init_policy(
            resources=[Resource(f"drn:document:{self.tenant_id()}:/{self.id()}/*")],
            actions=[Action("List*"), Action("Get*")],
        )

    def _is_user_invited(self, user_id: EntityId) -> bool:
        raise NotImplementedError

    def _is_group_has_user(self, user_id: EntityId) -> bool:
        return user_id in self.users

    class _PolicyFactory:
        @classmethod
        def make_init_policy(cls, resources: list[Resource], actions: list[Action]) -> Policy:
            return Policy(
                id_=EntityId(),
                statements=[StatementBuilder().for_resources(resources).allow_actions(actions).build()],
            )
