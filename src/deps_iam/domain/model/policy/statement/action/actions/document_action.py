from enum import StrEnum

__all__ = ["DocumentAction"]


class DocumentAction(StrEnum):
    GET_DOCUMENT = "GetDocument"
    GET_STATUS = "GetStatus"
    GET_DOCUMENT_METADATA = "GetDocumentMetadata"
    RUN_LAST_STEP = "RunLastStep"
    ADD_COMMENT = "AddComment"
    LIST_PREPROCESSED_IMAGES = "ListPreprocessedImages"
    ADD_LABEL = "AddLabel"
    REMOVE_DOCUMENT = "RemoveDocument"
    GET_FILE_CONTENT = "GetFileContent"
    LIST_STATES = "ListStates"
    LIST_FILES = "ListFiles"
    REMOVE_DOCUMENT_LABEL = "RemoveDocumentLabel"
    RUN_PIPELINE = "RunPipeline"
    RUN_PIPELINE_FROM_STEP = "RunPipelineFromStep"
    REMOVE_DOCUMENT_REVIEW = "RemoveDocumentReview"
    CREATE_DOCUMENT_REVIEW = "CreateDocumentReview"
    REMOVE_DOCUMENT_REVIEWER = "RemoveDocumentReviewer"
    ADD_TYPE = "AddType"
    CREATE_UPLOAD_SESSION = "CreateUploadSession"
    CREATE_DOCUMENT = "CreateDocument"
    RUN_EXTRACTION = "RunExtraction"
    UPDATE_DOCUMENTS = "UpdateDocuments"
    UPDATE_DOCUMENT = "UpdateDocument"
    RUN_VALIDATION = "RunValidation"
    LIST_LABELS = "ListLabels"
    CREATE_LABELS = "CreateLables"
    LIST_DOCUMENTS = "ListDocuments"
    CREATE_DOCUMENTS = "CreateDocuments"
    REMOVE_DOCUMENTS = "RemoveDocuments"
    GET_STATES_STATISTICS = "GetStatesStatistics"
    LIST_RELATIONS = "ListRelations"
    CREATE_RELATIONS = "CreateRelations"
    CREATE_ASSIGNMENT = "CreateAssignment"
    REMOVE_ASSIGNMENT = "RemoveAssignment"
    UPDATE_ASSIGNMENT = "UpdateAssignment"
    LIST_DOCUMENT_CHILDREN = "ListDocumentChildren"
    LIST_ASSIGNNED_DOCUMENTS = "ListAssignedDocuments"
    LIST_RELATION_TYPES = "ListRelationTypes"
    CREATE_RELATION_TYPE = "CreateRelationType"
    UPDATE_RELATION_TYPE = "UpdateRelationType"
    UPDATE_RELATION = "UpdateRelation"
    CREATE_RELATION = "CreateRelation"
    REMOVE_RELATION_DOCUMENTS = "RemoveRelationDocuments"

    @classmethod
    def read_only_actions(cls) -> tuple[str, ...]:
        return (  # noqa; WPS227
            cls.GET_DOCUMENT,
            cls.GET_DOCUMENT_METADATA,
            cls.GET_STATUS,
            cls.LIST_PREPROCESSED_IMAGES,
            cls.GET_FILE_CONTENT,
            cls.LIST_STATES,
            cls.LIST_FILES,
            cls.LIST_LABELS,
            cls.LIST_DOCUMENTS,
            cls.GET_STATES_STATISTICS,
            cls.LIST_RELATIONS,
            cls.LIST_DOCUMENT_CHILDREN,
            cls.LIST_ASSIGNNED_DOCUMENTS,
            cls.LIST_RELATION_TYPES,
            cls.LIST_LABELS,
        )

    @classmethod
    def actions_affecting_the_document(cls) -> tuple[str, ...]:
        return (  # noqa; WPS227
            cls.ADD_COMMENT,
            cls.ADD_LABEL,
            cls.REMOVE_DOCUMENT,
            cls.REMOVE_DOCUMENT_LABEL,
            cls.RUN_PIPELINE,
            cls.RUN_PIPELINE_FROM_STEP,
            cls.RUN_LAST_STEP,
            cls.REMOVE_DOCUMENT_REVIEW,
            cls.REMOVE_DOCUMENT_REVIEWER,
            cls.ADD_TYPE,
            cls.RUN_EXTRACTION,
            cls.UPDATE_DOCUMENTS,
            cls.UPDATE_DOCUMENT,
            cls.RUN_VALIDATION,
            cls.CREATE_DOCUMENTS,
            cls.REMOVE_DOCUMENTS,
            cls.CREATE_RELATIONS,
            cls.CREATE_ASSIGNMENT,
            cls.REMOVE_ASSIGNMENT,
            cls.UPDATE_RELATION,
            cls.CREATE_RELATION,
            cls.REMOVE_RELATION_DOCUMENTS,
            cls.CREATE_RELATION_TYPE,
            cls.UPDATE_RELATION_TYPE,
            cls.CREATE_DOCUMENT_REVIEW,
        )
