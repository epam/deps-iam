from enum import StrEnum

__all__ = ["UnifierAction"]


class UnifierAction(StrEnum):
    GET_UNIFIED_DATA = "GetUnifiedData"
    UPDATE_UNIFIED_DATA = "UpdateUnifiedData"
    RUN_TRANSFORMATIONS = "RunTransformations"
    LIST_CELLS = "ListCells"
    ADD_CELLS = "AddCells"
