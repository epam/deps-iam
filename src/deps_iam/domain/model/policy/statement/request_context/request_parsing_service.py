import re
from typing import Any, Mapping

from deps_iam.domain.exceptions import NotFoundError

from .mappers.corleone_mapper import corleone_mapper
from .mappers.document_mapper import document_mapper
from .mappers.document_type_mapper import document_type_mapper
from .mappers.extraction_mapper import extraction_mapper
from .mappers.file_storage_mapper import file_storage_mapper
from .mappers.iam_mapper import iam_mapper
from .mappers.ocr_mapper import ocr_mapper
from .mappers.parsed_data_mapper import parsed_data_mapper
from .mappers.preprocess_mapper import preprocess_mapper
from .mappers.request_mapper import RawRequestContext, RequestInfo
from .mappers.tables_mapper import tables_mapper
from .mappers.unifier_mapper import unifier_mapper
from .mappers.validation_mapper import validation_mapper
from .parsed_request import ParsedRequest
from .request_context import RequestContext
from .service_name import ServiceName

__all__ = ["RequestParsingService"]


class RequestParsingService:
    def __init__(self):
        self.service_parsers = {
            ServiceName.DOCUMENT: document_mapper,
            ServiceName.CORLEONE: corleone_mapper,
            ServiceName.PREPROCESS: preprocess_mapper,
            ServiceName.OCR: ocr_mapper,
            ServiceName.VALIDATION: validation_mapper,
            ServiceName.FILE_STORAGE: file_storage_mapper,
            ServiceName.TABLES: tables_mapper,
            ServiceName.PARSED_DATA: parsed_data_mapper,
            ServiceName.IAM: iam_mapper,
            ServiceName.UNIFIER: unifier_mapper,
            ServiceName.EXTRACTION: extraction_mapper,
            ServiceName.DOCUMENT_TYPE: document_type_mapper,
        }

    def parse_request(self, request_headers: Mapping[str, Any], body: str, user_subject: str) -> RequestContext:
        parsed_request = ParsedRequest(request_headers, body)
        request_mapper = self.service_parsers[ServiceName(parsed_request.service)]
        return self._parse_service_request(parsed_request, user_subject, request_mapper)

    @staticmethod
    def _parse_service_request(
        parsed_request: ParsedRequest, user_subject: str, request_mapper: dict[RequestInfo, RawRequestContext]
    ) -> RequestContext:
        def filter_by_path_and_method(request_mapper_item):
            return (
                re.search(request_mapper_item[0].path_regex, parsed_request.base_path)
                and request_mapper_item[0].method == parsed_request.method
            )

        try:
            match = next(filter(filter_by_path_and_method, request_mapper.items()))

        except StopIteration:
            raise NotFoundError("Endpoint not found")

        return RequestContext.from_parsed_request(match, user_subject, parsed_request)
