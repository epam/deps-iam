from .action import Action
from .effect import Effect
from .principal import Principal
from .resource import Resource
from .statement import Statement

__all__ = ["StatementBuilder"]


class StatementBuilder:
    def __init__(self) -> None:
        self._principals: list[Principal] = []
        self._resources: list[Resource] = []

    @property
    def effect(self) -> Effect:
        return self._effect

    @effect.setter
    def effect(self, effect: Effect):
        if hasattr(self, "effect"):
            raise RuntimeError("Effect has been set already. Can't change effect for StatementBuilder.")
        self._effect = effect

    @property
    def actions(self) -> list[Action]:
        return self._actions

    @actions.setter
    def actions(self, actions: list[Action]) -> None:
        if hasattr(self, "actions"):
            raise RuntimeError("Actions has been set already. Can't change actions for StatementBuilder.")
        self._actions = actions

    def for_principals(self, principals: list[Principal]) -> "StatementBuilder":
        self._principals = principals
        return self

    def for_resources(self, resources: list[Resource]) -> "StatementBuilder":
        self._resources = resources
        return self

    def allow_all_actions(self) -> "StatementBuilder":
        self.actions = [Action("*")]
        self._effect = Effect.ALLOW
        return self

    def allow_actions(self, actions: list[Action]) -> "StatementBuilder":
        self.actions = actions
        self.effect = Effect.ALLOW
        return self

    def deny_actions(self, actions: list[Action]) -> "StatementBuilder":
        self.effect = Effect.DENY
        self.actions = actions
        return self

    def build(self) -> Statement:
        return Statement(self._effect, self._actions, self._resources, self._principals)
