import re

from ....shared.guards import Guard, ImmutableCheck
from .principal import Principal

__all__ = ["PrincipalMatchSpecification"]


class PrincipalMatchSpecification:
    principal = Guard[Principal](Principal, ImmutableCheck())

    def __init__(self, principal: Principal) -> None:
        self.principal = principal

    @property
    def pattern(self) -> re.Pattern:
        return re.compile(
            re.sub(
                r"\*",
                r".*",
                self.principal(),
            )
        )

    def __str__(self) -> str:
        return f"<PrincipalSpecification> principal: {self.principal}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.principal == other.principal

    def is_satisfied_by(self, principal: "Principal") -> bool:
        return True if self.pattern.match(principal.value) else False
