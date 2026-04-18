from . import RequestContext, RequestStatement
from .policy import Policy
from .policy_decision import PolicyDecision

__all__ = ["PermissionDeterminingService"]


class PermissionDeterminingService:
    def __init__(self, policies: dict[str, list[Policy]], request_context: RequestContext) -> None:
        self._policies = policies
        self._request_context = request_context

    @property
    def statement_decisions(self) -> dict[str, PolicyDecision]:
        if not hasattr(self, "_statement_decisions"):
            self._statement_decisions = {
                request_statement.resource(): self._determine_permission(request_statement)
                for request_statement in self._request_context.request_statements
            }
        return self._statement_decisions

    @property
    def denied_resources(self) -> list[str]:
        return [
            resource
            for resource, decision in self.statement_decisions.items()
            if decision in {PolicyDecision.EXPLICIT_DENY, PolicyDecision.IMPLICIT_DENY}
        ]

    @property
    def has_permission(self) -> bool:
        return True if self._is_allowed and not self._is_denied else False

    @property
    def _is_denied(self) -> bool:
        return PolicyDecision.EXPLICIT_DENY in self.statement_decisions.values()

    @property
    def _is_allowed(self) -> bool:
        return all(PolicyDecision.ALLOW == decision for decision in self.statement_decisions.values())

    def _determine_permission(self, rs: RequestStatement) -> PolicyDecision:
        decisions = {
            policy.evaluate(rs)
            for resource, policies in self._policies.items()
            if resource in rs.all_resources
            for policy in policies
        }

        if PolicyDecision.EXPLICIT_DENY in decisions:
            return PolicyDecision.EXPLICIT_DENY

        if PolicyDecision.ALLOW in decisions:
            return PolicyDecision.ALLOW

        return PolicyDecision.IMPLICIT_DENY
