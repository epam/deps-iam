from enum import StrEnum

__all__ = ["ExtractionAction"]


class ExtractionAction(StrEnum):
    LIST_EXTRACTED_DATA = "ListExtractedData"
    GET_EXTRACTED_DATA = "GetExtractedData"
    UPDATE_EXTRACTED_DATA = "UpdateExtractedData"
    REMOVE_EXTRACTED_DATA = "RemoveExtractedData"
    ADD_EXTRACTED_FIELD = "AddExtractedField"
    REMOVE_EXTRACTED_FIELD = "RemoveExtractedField"
    ADD_TABLE_INFO = "AddTableInfo"
    ADD_TABLE_CHUNKED_DATA = "AddTableChunkedData"
    GET_FIELD_CHUNK = "GetFieldChunk"
    UPDATE_EXTRACTED_FIELD = "UpdateExtractedField"
