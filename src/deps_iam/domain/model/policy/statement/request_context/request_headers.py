from enum import StrEnum

__all__ = ["RequestHeaders"]


class RequestHeaders(StrEnum):
    ORIGINAL_METHOD = "x-original-method"
    ORIGINAL_PATH = "x-original-path"
    ORIGINAL_QUERY = "x-original-query"
