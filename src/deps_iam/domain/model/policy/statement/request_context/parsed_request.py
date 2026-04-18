import json
from typing import Any, Mapping

from .body_resource import (
    BodyResource,
    CorleoneBodyResource,
    DocumentBodyResource,
    DocumentTypeBodyResourse,
    OCRBodyResource,
    ParsedDataBodyResourse,
    PreprocessBodyResource,
    TablesBodyResourse,
    UnifierBodyResourse,
    ValidationBodyResource,
)
from .request_headers import RequestHeaders
from .service_name import ServiceName

__all__ = ["ParsedRequest"]


class ParsedRequest:
    MAXSPLIT = 4
    SERVICE_INDEX = 2
    BASE_PATH_INDEX = -1

    def __init__(self, request_headers: Mapping[str, Any], body: str):
        self.request_headers = request_headers
        self.body = body

        self.body_resource_builders = {
            ServiceName.DOCUMENT: self._build_document_body_resource,
            ServiceName.CORLEONE: self._build_corleone_body_resource,
            ServiceName.PREPROCESS: self._build_preprocess_body_resource,
            ServiceName.OCR: self._build_ocr_body_resource,
            ServiceName.VALIDATION: self._build_validation_body_resource,
            ServiceName.TABLES: self._build_tables_body_resourse,
            ServiceName.PARSED_DATA: self._build_parsed_data_body_resourse,
            ServiceName.UNIFIER: self._build_unifier_body_resourse,
            ServiceName.DOCUMENT_TYPE: self._build_document_type_body_resourse,
        }

    @property
    def method(self) -> str:
        if method := self.request_headers.get(RequestHeaders.ORIGINAL_METHOD):
            return method

        raise RuntimeError("Method is not provided!")

    @property
    def path(self) -> str:
        if path := self.request_headers.get(RequestHeaders.ORIGINAL_PATH):
            return path

        raise RuntimeError("Path is not provided!")

    @property
    def query(self) -> str:
        if (query := self.request_headers.get(RequestHeaders.ORIGINAL_QUERY)) is None:
            raise RuntimeError("Query is not provided!")

        return query

    @property
    def path_splitted(self) -> list[str]:
        return self.path.split("/", self.MAXSPLIT)

    @property
    def service(self) -> str:
        return self.path_splitted[self.SERVICE_INDEX]

    @property
    def base_path(self) -> str:
        return self.path_splitted[self.BASE_PATH_INDEX]

    @property
    def body_resource(self) -> BodyResource:
        return self.body_resource_builders[self.service](self._build_body())  # type: ignore

    @staticmethod
    def _build_document_body_resource(body: Any) -> DocumentBodyResource:
        document_id = [body.get("documentId")] if body.get("documentId") else []
        document_ids = body.get("documentIds", [])
        assigned_documents = body.get("assignedDocuments", [])
        document = [body.get("document")] if body.get("document") else []
        label_id = [body.get("labelId")] if body.get("labelId") else []

        return DocumentBodyResource(
            document=document_id or document_ids or assigned_documents or document, label=label_id
        )

    @staticmethod
    def _build_corleone_body_resource(body: Any) -> CorleoneBodyResource:
        document = [body.get("documentId")] if body.get("documentId") else []

        return CorleoneBodyResource(document=document)

    @staticmethod
    def _build_preprocess_body_resource(body: Any) -> PreprocessBodyResource:
        document = [body.get("documentId")] if body.get("documentId") else []

        return PreprocessBodyResource(document=document)

    @staticmethod
    def _build_ocr_body_resource(body: Any) -> OCRBodyResource:
        blob_file = [body.get("blobFile")] if body.get("blobFile") else []

        return OCRBodyResource(blob_file=blob_file)

    @staticmethod
    def _build_validation_body_resource(body: Any) -> ValidationBodyResource:
        document = [body_dict.get("document_id") for body_dict in body]

        return ValidationBodyResource(document=document)

    @staticmethod
    def _build_tables_body_resourse(body: Any) -> TablesBodyResourse:
        blob_file = [body.get("blobFile")] if body.get("blobFile") else []

        return TablesBodyResourse(blob_file=blob_file)

    @staticmethod
    def _build_parsed_data_body_resourse(body: Any) -> ParsedDataBodyResourse:
        document = [body.get("documentId")] if body.get("documentId") else []

        return ParsedDataBodyResourse(document=document)

    @staticmethod
    def _build_unifier_body_resourse(body: Any) -> UnifierBodyResourse:
        document = [body.get("documentId")] if body.get("documentId") else []

        return UnifierBodyResourse(document=document)

    @staticmethod
    def _build_document_type_body_resourse(body: Any) -> DocumentTypeBodyResourse:
        type_from_body = body.get("document_type") or body.get("documentType")
        document_type = [type_from_body] if type_from_body else []

        return DocumentTypeBodyResourse(document_type=document_type)

    def _build_body(self) -> Any:
        return json.loads(self.body)
