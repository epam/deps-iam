from ..policy import Policy
from ..shared import EntityId, EntityName
from ..shared.guards import Guard, ImmutableCheck

__all__ = ["Role"]


class Role:
    group_id = Guard[EntityId](EntityId, ImmutableCheck())
    name = Guard[EntityName](EntityName, ImmutableCheck())
    policy = Guard[Policy](Policy, ImmutableCheck())

    def __init__(self, group_id: EntityId, name: EntityName, policy: Policy) -> None:
        self.group_id = group_id
        self.name = name
        self.policy = policy

    @property
    def drn(self) -> str:
        return self.name.drn

    def __str__(self) -> str:
        return f"<Role> group_id: {self.group_id}, name: {self.name}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__) and self.name == other.name and self.group_id == other.group_id
        )  # noqa: WPS221
