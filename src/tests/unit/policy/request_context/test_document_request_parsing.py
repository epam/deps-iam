import json

import pytest

from deps_iam.domain.exceptions import NotFoundError
from tests.unit.policy.conftest import USER_SUBJECT


class TestDocumentRequestParsing:
    def test__resource_in_body__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/document/v1/documents/add-comment",
            "x-original-query": "",
        }
        body = json.dumps({"documentId": "11", "text": "comment"})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "AddComment"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["11"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__two_resources_in_body__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/document/v1/documents/add-label",
            "x-original-query": "",
        }
        body = json.dumps({"documentIds": ["11", "22"], "labelId": "label_name"})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "AddLabel"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["11", "22"], "label": ["label_name"]}
        assert [r.value for r in request_context.resources] == ["document", "label"]

    def test__resource_in_path__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/document/v1/documents/11/preprocessed-images",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListPreprocessedImages"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["11"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__resource_in_query__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/document/v1/files/file-content",
            "x-original-query": "blob=filepath",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetFileContent"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"file_path": ["filepath"]}
        assert [r.value for r in request_context.resources] == ["file_path"]

    def test__empty_resource__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/document/v1/documents",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListDocuments"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__no_method_header__raise_error(self, request_parser):
        request_headers = {"x-original-path": "/api/document/v1/documents", "x-original-query": ""}
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
            "x-original-path": "/api/document/v1/files/file-content",
        }
        body = json.dumps({})
        with pytest.raises(RuntimeError):
            request_parser.parse_request(request_headers, body, USER_SUBJECT)

    def test__empty_method_header__raise_error(self, request_parser):
        request_headers = {
            "x-original-method": "",
            "x-original-path": "/api/document/v1/documents/add-comment",
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
            "x-original-path": "/api/document/v1/some/path",
            "x-original-query": "",
        }
        body = json.dumps({})
        with pytest.raises(NotFoundError):
            request_parser.parse_request(request_headers, body, USER_SUBJECT)
