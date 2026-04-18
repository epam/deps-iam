from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

preprocess_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("GET", "^preprocessed-data/([0-9]*)$"): RawRequestContext(
        "GetPreprocessedData", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^preprocessed-table-data/([0-9]*)/(.*)$"): RawRequestContext(
        "GetPreprocessedTableData", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^unified_data/([0-9]*)$"): RawRequestContext(
        "GetUnifiedData", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^unified_data/upsert-data$"): RawRequestContext(
        "UpdateUnifiedData", ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("PATCH", "^unified_data/([0-9]*)/add-element$"): RawRequestContext(
        "UpdateUnifiedDataElement", ["document"], ResourceSource.PATH, [1]
    ),
}
