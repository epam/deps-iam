from ...action import DocumentAction
from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

document_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("GET", "^files/file-content$"): RawRequestContext(
        DocumentAction.GET_FILE_CONTENT, ["file_path"], ResourceSource.QUERY, ["blob"]
    ),
    RequestInfo("GET", "^documents/states$"): RawRequestContext(DocumentAction.LIST_STATES, ["document"], None, []),
    RequestInfo("POST", "^documents/add-comment$"): RawRequestContext(
        DocumentAction.ADD_COMMENT, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("GET", "^documents/([0-9]*)/preprocessed-images$"): RawRequestContext(
        DocumentAction.LIST_PREPROCESSED_IMAGES, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^documents/([0-9]*)/files$"): RawRequestContext(
        DocumentAction.LIST_FILES, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("POST", "^documents/add-label$"): RawRequestContext(
        DocumentAction.ADD_LABEL, ["document", "label"], ResourceSource.BODY, ["document", "label"]
    ),
    RequestInfo("POST", "^documents/remove-label$"): RawRequestContext(
        DocumentAction.REMOVE_DOCUMENT_LABEL, ["document", "label"], ResourceSource.BODY, ["document", "label"]
    ),
    RequestInfo("POST", "^documents/run-pipeline$"): RawRequestContext(
        DocumentAction.RUN_PIPELINE, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("POST", "^documents/run-pipeline-from-step$"): RawRequestContext(
        DocumentAction.RUN_PIPELINE_FROM_STEP, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("POST", "^documents/retry-last-step$"): RawRequestContext(
        DocumentAction.RUN_LAST_STEP, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("POST", "^documents/complete$"): RawRequestContext(
        DocumentAction.REMOVE_DOCUMENT_REVIEW, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("POST", "^documents/start-review$"): RawRequestContext(
        DocumentAction.CREATE_DOCUMENT_REVIEW, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("POST", "^documents/reset-reviewer$"): RawRequestContext(
        DocumentAction.REMOVE_DOCUMENT_REVIEWER, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("POST", "^documents/assign-type$"): RawRequestContext(
        DocumentAction.ADD_TYPE, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("POST", "^documents/multi-upload-session$"): RawRequestContext(
        DocumentAction.CREATE_UPLOAD_SESSION, [], None, []
    ),
    RequestInfo("POST", "^documents/document-file$"): RawRequestContext(
        DocumentAction.CREATE_DOCUMENT, ["document"], None, []
    ),
    RequestInfo("POST", "^documents/extract-data$"): RawRequestContext(
        DocumentAction.RUN_EXTRACTION, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("GET", "^documents/([0-9]*)$"): RawRequestContext(
        DocumentAction.GET_DOCUMENT, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PUT", "^documents/([0-9]*)$"): RawRequestContext(
        DocumentAction.UPDATE_DOCUMENTS, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^documents/([0-9]*)$"): RawRequestContext(
        DocumentAction.REMOVE_DOCUMENT, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PATCH", "^documents/([0-9]*)$"): RawRequestContext(
        DocumentAction.UPDATE_DOCUMENT, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^documents/([0-9]*)/status$"): RawRequestContext(
        DocumentAction.GET_STATUS, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("POST", "^documents/validate$"): RawRequestContext(
        DocumentAction.RUN_VALIDATION, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("GET", "^documents/([0-9]*)/metadata$"): RawRequestContext(
        DocumentAction.GET_DOCUMENT_METADATA, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^labels$"): RawRequestContext(DocumentAction.LIST_LABELS, ["label"], None, []),
    RequestInfo("POST", "^labels$"): RawRequestContext(
        DocumentAction.CREATE_LABELS, ["label"], ResourceSource.BODY, ["label"]
    ),
    RequestInfo("GET", "^documents$"): RawRequestContext(DocumentAction.LIST_DOCUMENTS, ["document"], None, []),
    RequestInfo("PUT", "^documents$"): RawRequestContext(
        DocumentAction.UPDATE_DOCUMENTS, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("POST", "^documents$"): RawRequestContext(
        DocumentAction.CREATE_DOCUMENTS, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("DELETE", "^documents$"): RawRequestContext(
        DocumentAction.REMOVE_DOCUMENTS, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("GET", "^statistic/states/([0-9]*)$"): RawRequestContext(
        DocumentAction.GET_STATES_STATISTICS, ["document"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^relations/$"): RawRequestContext(
        DocumentAction.LIST_RELATIONS, ["document"], ResourceSource.QUERY, ["assignedDocuments"]
    ),
    RequestInfo("POST", "^relations/$"): RawRequestContext(
        DocumentAction.CREATE_RELATIONS, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("POST", "^relations/(.*)/(.*)/assign$"): RawRequestContext(
        DocumentAction.CREATE_ASSIGNMENT, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("DELETE", "^relations/(.*)/(.*)/assign$"): RawRequestContext(
        DocumentAction.REMOVE_ASSIGNMENT, ["document"], None, []
    ),
    RequestInfo("PATCH", "^relations/(.*)/(.*)/assign$"): RawRequestContext(
        DocumentAction.UPDATE_ASSIGNMENT, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("GET", "^relations/(.*)/(.*)/children$"): RawRequestContext(
        DocumentAction.LIST_DOCUMENT_CHILDREN, [], None, []
    ),
    RequestInfo("GET", "^relations/(.*)/(.*)/documents$"): RawRequestContext(
        DocumentAction.LIST_ASSIGNNED_DOCUMENTS, [], None, []
    ),
    RequestInfo("GET", "^relations/types$"): RawRequestContext(DocumentAction.LIST_RELATION_TYPES, [], None, []),
    RequestInfo("POST", "^relations/types$"): RawRequestContext(DocumentAction.CREATE_RELATION_TYPE, [], None, []),
    RequestInfo("PUT", "^relations/types/(.*)$"): RawRequestContext(DocumentAction.UPDATE_RELATION_TYPE, [], None, []),
    RequestInfo("GET", "^relations/(.*)/(.*)$"): RawRequestContext(DocumentAction.LIST_RELATION_TYPES, [], None, []),
    RequestInfo("PUT", "^relations/(?!.*types).*/(.*)$"): RawRequestContext(
        DocumentAction.UPDATE_RELATION, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("POST", "^relations/(.*)/(.*)$"): RawRequestContext(
        DocumentAction.CREATE_RELATION, ["document"], ResourceSource.BODY, ["document"]
    ),
    RequestInfo("DELETE", "^relations/(.*)/(.*)$"): RawRequestContext(
        DocumentAction.REMOVE_RELATION_DOCUMENTS, ["document"], ResourceSource.QUERY, ["doc_id"]
    ),
}
