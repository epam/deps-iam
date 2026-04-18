from typing import Any, Mapping, Sequence

from deps_iam.domain.model import (
    Action,
    Effect,
    EntityId,
    Policy,
    Principal,
    Resource,
    Statement,
)


class StatementMapper:
    @classmethod
    def from_dict(cls, statement_dict: Mapping[str, Any]) -> Statement:
        return Statement(
            effect=Effect(statement_dict["effect"]),
            actions=[Action(a) for a in statement_dict["actions"]],
            resources=[Resource(r) for r in statement_dict["resources"]],
            principals=[Principal(p) for p in statement_dict["principals"]]
            if statement_dict["principals"] is not None
            else None,
        )

    @classmethod
    def to_dict(cls, statement: Statement) -> dict[str, Any]:
        return {
            "effect": statement.effect.value,
            "actions": [a() for a in statement.actions],
            "resources": [r() for r in statement.resources],
            "principals": [p() for p in statement.principals] if statement.principals is not None else None,
        }


class PolicyMapper:
    @classmethod
    def to_dict(cls, policy: Policy) -> dict[str, Any]:
        return {"id": policy.id(), "statements": [StatementMapper.to_dict(st) for st in policy.statements]}

    @classmethod
    def from_dict(cls, policy_dict: Mapping[str, Any]) -> Policy:
        return Policy(
            id_=EntityId(policy_dict["id"]),
            statements=[StatementMapper.from_dict(st) for st in policy_dict["statements"]],
        )


class PolicyListMapper:
    @classmethod
    def from_dict(cls, pl_mapper: list[Mapping[str, Any]]) -> list[Policy]:
        return [PolicyMapper.from_dict(p) for p in pl_mapper]


class ResourcePolicyMapper:
    @classmethod
    def from_dict(cls, rp_mapping: Sequence[Mapping[str, Any]]) -> dict[str, list[Policy]]:
        return {rp["resource"]: PolicyListMapper.from_dict(rp["policies"]) for rp in rp_mapping}
