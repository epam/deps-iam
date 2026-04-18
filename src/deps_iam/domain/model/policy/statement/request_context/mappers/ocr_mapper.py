from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

ocr_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("POST", "^extract-area$"): RawRequestContext(
        "RunExtractionArea", ["blob_file"], ResourceSource.BODY, ["blob_file"]
    ),
    RequestInfo("POST", "^extract-text$"): RawRequestContext("RunExtractionText", [], None, []),
    RequestInfo("GET", "^engines$"): RawRequestContext("ListEngines", ["engine"], None, []),
}
