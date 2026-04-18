from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

file_storage_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("GET", "^file/(.*)$"): RawRequestContext("GetFile", ["path"], ResourceSource.PATH, [1]),
    RequestInfo("POST", "^file/(.*)$"): RawRequestContext("CreateFile", ["path"], ResourceSource.PATH, [1]),
    RequestInfo("DELETE", "^file/(.*)$"): RawRequestContext("RemoveFile", ["path"], ResourceSource.PATH, [1]),
    RequestInfo("POST", "^file$"): RawRequestContext("CreateFileNoPath", [], None, []),
}
