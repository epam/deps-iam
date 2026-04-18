from typing import Optional

from ..shared import EntityId
from ..shared.guards import Guard, ImmutableCheck
from .policy_decision import PolicyDecision
from .statement import (
    Action,
    Effect,
    Principal,
    RequestStatement,
    Resource,
    Statement,
    StatementMatchSpecification,
)

__all__ = ["Policy"]


class Policy:
    id = Guard[EntityId](EntityId, ImmutableCheck())
    statements = Guard[list[Statement]](list, ImmutableCheck())

    EFFECT_MAP = {
        Effect.ALLOW: PolicyDecision.ALLOW,
        Effect.DENY: PolicyDecision.EXPLICIT_DENY,
    }

    def __init__(
        self,
        id_: EntityId,
        *,
        statements: Optional[list[Statement]] = None,
    ) -> None:
        self.id = id_

        self.statements = statements if statements is not None else []

        self._specifications = [(statement, StatementMatchSpecification(statement)) for statement in self.statements]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    def __str__(self) -> str:
        return f"<Policy> id: {self.id}, statements count: {len(self.statements)}"

    @property
    def is_resource_based(self) -> bool:
        return all(statement.is_resource_based for statement in self.statements)

    def evaluate(self, request_statement: RequestStatement) -> PolicyDecision:
        for statement, specification in self._specifications:  # noqa: WPS503
            if specification.is_satisfied_by(request_statement):
                return self.EFFECT_MAP[statement.effect]
        else:
            return PolicyDecision.IMPLICIT_DENY

    def add_statement(
        self,
        effect: str,
        actions: list[str],
        resources: list[str],
        principals: list[str],
    ) -> None:
        self.statements.append(
            Statement(
                effect=Effect(effect),
                actions=[Action(action) for action in actions],
                resources=[Resource(resource) for resource in resources],
                principals=[Principal(principal) for principal in principals],
            )
        )
