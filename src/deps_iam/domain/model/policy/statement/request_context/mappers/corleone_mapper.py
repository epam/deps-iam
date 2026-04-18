from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

corleone_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("PUT", "^plugins/register$"): RawRequestContext("CreatePlugin", ["document_type"], None, []),
    RequestInfo("GET", "^types$"): RawRequestContext("ListTypes", ["document_type"], ResourceSource.QUERY, ["code"]),
    RequestInfo("POST", "^types$"): RawRequestContext("CreateType", ["document_type"], None, []),
    RequestInfo("GET", "^types/(.*)$"): RawRequestContext("GetType", ["document_type"], ResourceSource.PATH, [1]),
    RequestInfo("DELETE", "^types/(.*)$"): RawRequestContext("RemoveType", ["document_type"], ResourceSource.PATH, [1]),
    RequestInfo("GET", "^types/(.*)/blob-files$"): RawRequestContext(
        "ListTypeBlobFiles", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^types/(.*)/fields$"): RawRequestContext(
        "ListTypeFields", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("POST", "^types/(.*)/fields$"): RawRequestContext(
        "CreateTypeField", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^types/(.*)/fields/(.*)$"): RawRequestContext(
        "GetTypeField", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^types/(.*)/fields/(.*)$"): RawRequestContext(
        "UpdateTypeField", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^types/(.*)/fields/(.*)$"): RawRequestContext(
        "RemoveTypeField", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^types/(.*)/models$"): RawRequestContext(
        "ListTypeModels", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^types/(.*)/models$"): RawRequestContext(
        "UpdateTypeModel", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("POST", "^types/(.*)/models$"): RawRequestContext(
        "CreateTypeModel", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^types/(.*)/models$"): RawRequestContext(
        "RemoveTypeModels", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^types/(.*)/models/(.*)$"): RawRequestContext(
        "GetTypeModel", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^types/(.*)/models/(.*)$"): RawRequestContext(
        "RemoveTypeModel", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^types/(.*)/models/(.*)/templates/(.*)/fields$"): RawRequestContext(
        "UpdateTypeModelTemplateFields", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("POST", "^types/(.*)/models/templates$"): RawRequestContext(
        "CreateTypeModelTemplate", ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^extracted-data/$"): RawRequestContext(
        "ListExtractedData", ["document_type"], ResourceSource.QUERY, ["document_type"]
    ),
    RequestInfo("GET", "^extracted-data/([0-9]*)$"): RawRequestContext(
        "GetExtractedData", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^extracted-data/([0-9]*)$"): RawRequestContext(
        "UpdateExtractedData", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^extracted-data/([0-9]*)$"): RawRequestContext(
        "RemoveExtractedData", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^extracted-data/([0-9]*)/export$"): RawRequestContext(
        "RunExport", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^extracted-data/([0-9]*)/field$"): RawRequestContext(
        "UpdateExtractedDataFields", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^extracted-data/([0-9]*)/fields/([0-9]*)/table/info$"): RawRequestContext(
        "UpdateExtractedDataFieldTableInfo", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^extracted-data/([0-9]*)/fields/([0-9]*)/table/chunk$"): RawRequestContext(
        "UpdateExtractedDataFieldTableChunk", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^extracted-data/([0-9]*)/fields/([0-9]*)/chunk$"): RawRequestContext(
        "GetExtractedDataFieldChunk", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PATCH", "^extracted-data/([0-9]*)/fields/([0-9]*)$"): RawRequestContext(
        "UpdateExtractedDataField", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^extracted-data/([0-9]*)/fields$"): RawRequestContext(
        "RemoveExtractedDataFields", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^parsed-data/([0-9]*)$"): RawRequestContext(
        "ListParsedData", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("POST", "^extract$"): RawRequestContext(
        "RunExtraction", ["document"], ResourceSource.BODY, ["document"]
    ),
}
