import logging

from deps_iam.domain.model import EntityId, Policy, Principal, Resource, Statement

from .statement.statement_builder import StatementBuilder

__all__ = ["ResourceBasedPolicyFactory"]


class ResourceBasedPolicyFactory:
    _logger = logging.getLogger("PolicyFactory")

    @classmethod
    def create_reviewer_assignment(cls, resource: Resource, reviewer: Principal) -> Policy:
        statement = StatementBuilder().for_principals([reviewer]).for_resources([resource]).allow_all_actions().build()
        return cls._build_policy([statement])

    @classmethod
    def _build_policy(cls, statements: list[Statement]) -> Policy:
        cls._logger.debug("Create resource based policy with statements: %s", *statements)
        return Policy(EntityId(), statements=statements)
