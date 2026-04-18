from typing import Optional

from ...shared.guards import Guard, ImmutableCheck
from .action import Action
from .effect import Effect
from .principal import Principal
from .resource import Resource

__all__ = ["Statement"]


class Statement:
    effect = Guard[Effect](Effect, ImmutableCheck())
    actions = Guard[list[Action]](list, ImmutableCheck())
    resources = Guard[list[Resource]](list, ImmutableCheck())
    principals = Guard[list[Principal]](list, ImmutableCheck())

    def __init__(
        self,
        effect: Effect,
        actions: list[Action],
        resources: list[Resource],
        principals: Optional[list[Principal]] = None,
    ) -> None:
        self.effect = effect
        self.actions = actions
        self.resources = resources
        self.principals = principals if principals is not None else []

    def __str__(self) -> str:
        return (
            f"<Statement> effect: {self.effect},"
            f"actions count: {len(self.actions)}, "
            f"resources count: {len(self.resources)}, "
            f"principal count: {len(self.principals)}"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)  # noqa: WPS222
            and self.effect == other.effect
            and self.actions == other.actions
            and self.resources == other.resources
            and self.principals == other.principals
        )

    @property
    def is_resource_based(self) -> bool:
        return True if self.principals else False

    @property
    def is_allow(self) -> bool:
        return self.effect == Effect.ALLOW

    @property
    def is_deny(self) -> bool:
        return self.effect == Effect.DENY
