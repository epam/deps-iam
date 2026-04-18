from ..shared import EntityName
from ..shared.guards import Guard, ImmutableCheck

__all__ = ["GroupInfo"]


class GroupInfo:
    group = Guard[EntityName](EntityName, ImmutableCheck())
    role = Guard[EntityName](EntityName, ImmutableCheck())

    def __init__(self, group: EntityName, role: EntityName) -> None:
        self.group = group
        self.role = role

    def __str__(self) -> str:
        return f"<GroupInfo> group: {self.group}, role: {self.role}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__) and self.group == other.group and self.role == other.role
        )  # noqa: WPS221

    @property
    def group_drn(self) -> str:
        return self.group.drn

    @property
    def role_drn(self) -> str:
        return self.role.drn
