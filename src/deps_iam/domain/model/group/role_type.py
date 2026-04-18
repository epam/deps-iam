from enum import StrEnum

__all__ = ["RoleType"]


class RoleType(StrEnum):
    OWNER = "owner"
    USER = "user"
