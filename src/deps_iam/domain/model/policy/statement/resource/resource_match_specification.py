import re

from ....shared.guards import Guard, ImmutableCheck
from .resource import Resource

__all__ = ["ResourceMatchSpecification"]


class ResourceMatchSpecification:
    resource = Guard[Resource](Resource, ImmutableCheck())

    def __init__(self, resource: Resource) -> None:
        self.resource = resource

    @property
    def pattern(self) -> re.Pattern:
        return re.compile(
            re.sub(
                r"\*",
                r".*",
                self.resource(),
            )
        )

    def __str__(self) -> str:
        return f"<ResourceSpecification> resource: {self.resource}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.resource == other.resource

    def is_satisfied_by(self, resource: "Resource") -> bool:
        return True if self.pattern.match(resource.value) else False
