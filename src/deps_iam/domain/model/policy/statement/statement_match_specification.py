from ...shared.guards import Guard, ImmutableCheck
from .action import ActionMatchSpecification
from .principal import PrincipalMatchSpecification
from .request_statement import RequestStatement
from .resource import ResourceMatchSpecification
from .statement import Statement

__all__ = ["StatementMatchSpecification"]


class StatementMatchSpecification:
    statement = Guard[Statement](Statement, ImmutableCheck())

    def __init__(self, statement: Statement) -> None:
        self.statement = statement

        self._action_specs = [ActionMatchSpecification(action) for action in statement.actions]
        self._resource_specs = [ResourceMatchSpecification(resource) for resource in statement.resources]
        self._principal_specs = (
            [PrincipalMatchSpecification(principal) for principal in statement.principals]
            if statement.is_resource_based
            else None
        )

    def __str__(self) -> str:
        return f"<StatementSpecification> statement: {self.statement}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.statement == other.statement

    def is_satisfied_by(self, rs: RequestStatement) -> bool:
        actions_match = any(action_spec.is_satisfied_by(rs.action) for action_spec in self._action_specs)
        resources_match = any(resource_spec.is_satisfied_by(rs.resource) for resource_spec in self._resource_specs)
        principals_match = (
            any(principal_spec.is_satisfied_by(rs.principal) for principal_spec in self._principal_specs)
            if self._principal_specs
            else True
        )
        return all((actions_match, resources_match, principals_match))
