import logging

from ..group import Group, GroupInfo
from ..shared import EntityId
from ..shared.guards import Guard, ImmutableCheck
from .personal_info import PersonalInfo

__all__ = ["User"]


class User:
    id = Guard[EntityId](EntityId, ImmutableCheck())
    tenant_id = Guard[EntityId](EntityId, ImmutableCheck())
    personal_info = Guard[PersonalInfo](PersonalInfo)
    active_group = Guard[GroupInfo](GroupInfo)
    groups = Guard[dict[str, Group]](dict)

    def __init__(self, id_: EntityId, tenant_id: EntityId, personal_info: PersonalInfo):
        self.id = id_
        self.tenant_id = tenant_id
        self.personal_info = personal_info
        self.groups = {}
        self._logger = logging.getLogger(self.__class__.__name__)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    def __str__(self) -> str:
        return f"<User> id: {self.id}"

    @property
    def drn(self) -> str:
        return f"{self.active_group.role_drn}/user/{self.id()}"

    def join_group(self, group: Group) -> None:
        if not self.active_group:
            self.active_group = group.make_group_info(self.id())
        self.groups[group.id()] = group
