from enum import StrEnum

__all__ = ["DocumentTypeAction"]


class DocumentTypeAction(StrEnum):
    ADD_UNIFIER_PLUGIN = "AddUnifierPlugin"
    ADD_EXTRACTION_PLUGIN = "AddExtractionPlugin"
    LIST_TYPES = "ListTypes"
    ADD_TYPE = "AddType"
    GET_TYPE = "GetType"
    REMOVE_TEMPLATE = "RemoveTemplate"
