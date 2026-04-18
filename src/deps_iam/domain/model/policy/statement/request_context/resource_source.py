from enum import StrEnum

__all__ = ["ResourceSource"]


class ResourceSource(StrEnum):
    PATH = "path"
    BODY = "body"
    QUERY = "query"
