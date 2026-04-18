from ...action import DocumentTypeAction
from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

document_type_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("PUT", "^plugins/attach-unifier$"): RawRequestContext(
        DocumentTypeAction.ADD_UNIFIER_PLUGIN, ["document_type"], ResourceSource.BODY, ["document_type"]
    ),
    RequestInfo("PUT", "^plugins/attach-extraction$"): RawRequestContext(
        DocumentTypeAction.ADD_EXTRACTION_PLUGIN, ["document_type"], ResourceSource.BODY, ["document_type"]
    ),
    RequestInfo("GET", "^types$"): RawRequestContext(DocumentTypeAction.LIST_TYPES, ["document_type"], None, []),
    RequestInfo("POST", "^types$"): RawRequestContext(DocumentTypeAction.ADD_TYPE, ["document_type"], None, []),
    RequestInfo("GET", "^types/(.*)$"): RawRequestContext(
        DocumentTypeAction.GET_TYPE, ["document_type"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^types/(.*)$"): RawRequestContext(
        DocumentTypeAction.REMOVE_TEMPLATE, ["document_type"], ResourceSource.PATH, [1]
    ),
}
