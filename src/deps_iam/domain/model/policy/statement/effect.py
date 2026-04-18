from enum import Enum

__all__ = ["Effect"]


class Effect(Enum):
    ALLOW = "allow"
    DENY = "deny"
