import re

from ....shared.guards import Guard, ImmutableCheck
from .action import Action

__all__ = ["ActionMatchSpecification"]


class ActionMatchSpecification:
    action = Guard[Action](Action, ImmutableCheck())

    def __init__(self, action: Action) -> None:
        self.action = action

    @property
    def pattern(self) -> re.Pattern:
        return re.compile(
            re.sub(
                r"\*",
                r".*",
                f"{self.action()}$",
            )
        )

    def __str__(self) -> str:
        return f"<ActionSpecification> action: {self.action}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.action == other.action

    def is_satisfied_by(self, action: "Action") -> bool:
        return True if self.pattern.match(action.value) else False
