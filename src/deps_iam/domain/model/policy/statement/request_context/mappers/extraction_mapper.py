from ...action import ExtractionAction
from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

extraction_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("GET", "^extracted-data/$"): RawRequestContext(
        ExtractionAction.LIST_EXTRACTED_DATA, ["document"], None, []
    ),
    RequestInfo("GET", "^extracted-data/([0-9]*)$"): RawRequestContext(
        ExtractionAction.GET_EXTRACTED_DATA, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^extracted-data/([0-9]*)$"): RawRequestContext(
        ExtractionAction.UPDATE_EXTRACTED_DATA, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^extracted-data/([0-9]*)$"): RawRequestContext(
        ExtractionAction.REMOVE_EXTRACTED_DATA, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^extracted-data/([0-9]*)/field$"): RawRequestContext(
        ExtractionAction.ADD_EXTRACTED_FIELD, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^extracted-data/([0-9]*)/fields$"): RawRequestContext(
        ExtractionAction.REMOVE_EXTRACTED_FIELD, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^extracted-data/([0-9]*)/fields/(.*)/table/info$"): RawRequestContext(
        ExtractionAction.ADD_TABLE_INFO, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^extracted-data/([0-9]*)/fields/(.*)/table/chunk$"): RawRequestContext(
        ExtractionAction.ADD_TABLE_CHUNKED_DATA, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^extracted-data/([0-9]*)/fields/(.*)/chunk$"): RawRequestContext(
        ExtractionAction.GET_FIELD_CHUNK, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PATCH", "^extracted-data/([0-9]*)/fields/(.*)$"): RawRequestContext(
        ExtractionAction.UPDATE_EXTRACTED_FIELD, ["document"], ResourceSource.PATH, [1]
    ),
}
