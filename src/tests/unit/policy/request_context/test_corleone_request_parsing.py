import json

import pytest

from deps_iam.domain.exceptions import NotFoundError
from tests.unit.policy.conftest import USER_SUBJECT


class TestCorleoneRequestParsing:
    def test__resource_in_body__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/corleone/v1/extract",
            "x-original-query": "",
        }
        body = json.dumps(
            {
                "documentId": 1,
                "language": "eng",
                "engine": "TESSERACT",
                "extractionParams": {
                    "ocr": False,
                    "tables": False,
                    "ner": False,
                    "ocrEngine": "EASYOCR",
                    "tableDetectionEngine": "TESSERACT",
                    "language": "eng",
                    "nerEntities": ["phone"],
                },
            }
        )
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RunExtraction"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": [1]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__resource_in_path__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/corleone/v1/types/doc_type",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetType"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document_type": ["doc_type"]}
        assert [r.value for r in request_context.resources] == ["document_type"]

    def test__resource_in_non_required_query__query_passed__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/corleone/v1/types",
            "x-original-query": "code=doc_type_code",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListTypes"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document_type": ["doc_type_code"]}
        assert [r.value for r in request_context.resources] == ["document_type"]

    def test__resource_in_non_required_query__query_not_passed__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/corleone/v1/types",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListTypes"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["document_type"]

    def test__empty_resource__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/corleone/v1/types",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "CreateType"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["document_type"]

    def test__no_method_header__raise_error(self, request_parser):
        request_headers = {"x-original-path": "/api/corleone/v1/types", "x-original-query": ""}
        body = json.dumps({})
        with pytest.raises(RuntimeError):
            request_parser.parse_request(request_headers, body, USER_SUBJECT)

    def test__no_path_header__raise_error(self, request_parser):
        request_headers = {"x-original-method": "GET", "x-original-query": ""}
        body = json.dumps({})
        with pytest.raises(RuntimeError):
            request_parser.parse_request(request_headers, body, USER_SUBJECT)

    def test__no_query_header__raise_error(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/corleone/v1/types",
        }
        body = json.dumps({})
        with pytest.raises(RuntimeError):
            request_parser.parse_request(request_headers, body, USER_SUBJECT)

    def test__empty_method_header__raise_error(self, request_parser):
        request_headers = {
            "x-original-method": "",
            "x-original-path": "/api/corleone/v1/types",
            "x-original-query": "",
        }
        body = json.dumps({})
        with pytest.raises(RuntimeError):
            request_parser.parse_request(request_headers, body, USER_SUBJECT)

    def test__empty_path_header__raise_error(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "",
            "x-original-query": "",
        }
        body = json.dumps({})
        with pytest.raises(RuntimeError):
            request_parser.parse_request(request_headers, body, USER_SUBJECT)

    def test__non_existing_path__raise_error(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/corleone/v1/some/path",
            "x-original-query": "",
        }
        body = json.dumps({})
        with pytest.raises(NotFoundError):
            request_parser.parse_request(request_headers, body, USER_SUBJECT)
