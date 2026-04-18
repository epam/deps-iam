from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

parsed_data_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("GET", "^parsed-data/([0-9]*)$"): RawRequestContext(
        "GetParsedData", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^parsed-data/([0-9]*)$"): RawRequestContext(
        "RemoveParsedData", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^parsed-data$"): RawRequestContext(
        "UpdateParsedData", ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("PUT", "^parsed-data-item$"): RawRequestContext(
        "UpdateParsedDataItem", ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("GET", "^parsed-data/sources/(.*)$"): RawRequestContext("GetSourceParsedData", ["document"], None, []),
    RequestInfo("DELETE", "^parsed-data/sources/(.*)$"): RawRequestContext(
        "RemoveSourceParsedData", ["document"], None, []
    ),
}
