from enum import Enum

__all__ = ["PolicyDecision"]


class PolicyDecision(Enum):
    ALLOW = "allow"
    EXPLICIT_DENY = "explicit_deny"
    IMPLICIT_DENY = "implicit_deny"
