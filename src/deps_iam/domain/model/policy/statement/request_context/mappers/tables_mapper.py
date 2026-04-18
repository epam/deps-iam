from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

tables_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("POST", "^storage/detect$"): RawRequestContext(
        "RunDetectionTableStorage", ["blob_file"], ResourceSource.BODY, ["blob_file"]
    ),
    RequestInfo("POST", "^storage/extract$"): RawRequestContext(
        "RunExtractionTableStorage", ["blob_file"], ResourceSource.BODY, ["blob_file"]
    ),
    RequestInfo("POST", "^file/detect$"): RawRequestContext("RunDetectionTableFile", [], None, []),
    RequestInfo("GET", "^detection-engines$"): RawRequestContext("ListEngines", ["engine"], None, []),
}
