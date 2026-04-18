from ...shared.guards import Guard, ImmutableCheck
from .action import Action
from .principal import Principal
from .resource import Resource

__all__ = ["RequestStatement"]


class RequestStatement:
    action = Guard[Action](Action, ImmutableCheck())
    resource = Guard[Resource](Resource, ImmutableCheck())
    principal = Guard[Principal](Principal, ImmutableCheck())

    def __init__(
        self,
        action: Action,
        resource: Resource,
        principal: Principal,
    ) -> None:
        self.action = action
        self.resource = resource
        self.principal = principal

    def __str__(self) -> str:
        return (
            f"<RequestStatement> action: {self.action}," f"resource: {self.resource}, " f"principal: {self.principal}"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.action == other.action
            and self.resource == other.resource
            and self.principal == other.principal
        )

    @property
    def all_resources(self) -> list[str]:
        return [self.principal(), self.resource()]
