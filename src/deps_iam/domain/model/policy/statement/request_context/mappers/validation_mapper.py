from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

validation_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("POST", "^document-validation$"): RawRequestContext(
        "RunValidationDocument", ["document"], ResourceSource.QUERY, ["documentPk"]
    ),
    RequestInfo("POST", "^fields$"): RawRequestContext(
        "RunValidationFields", ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("GET", "^fields/business$"): RawRequestContext("ListFields", [], None, []),
    RequestInfo("POST", "^fields/business$"): RawRequestContext("CreateFields", [], None, []),
    RequestInfo("DELETE", "^fields/business/(.*)/(.*)$"): RawRequestContext("RemoveField", [], None, []),
    RequestInfo("GET", "^fields/business/(.*)/(.*)$"): RawRequestContext("GetField", [], None, []),
    RequestInfo("PATCH", "^fields/business/(.*)/(.*)$"): RawRequestContext("UpdateField", [], None, []),
    RequestInfo("GET", "^results/(.*)$"): RawRequestContext(
        "GetValidationResults", ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^rules$"): RawRequestContext("ListRules", [], None, []),
    RequestInfo("POST", "^rules$"): RawRequestContext("CreateRule", [], None, []),
    RequestInfo("DELETE", "^rules/([0-9]*)$"): RawRequestContext("RemoveRule", [], None, []),
    RequestInfo("GET", "^rules/([0-9]*)$"): RawRequestContext("GetRule", [], None, []),
    RequestInfo("PATCH", "^rules/([0-9]*)$"): RawRequestContext("UpdateRule", [], None, []),
}
