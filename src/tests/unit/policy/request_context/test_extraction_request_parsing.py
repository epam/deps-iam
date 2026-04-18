import json

import pytest

from deps_iam.domain.model.policy.statement.action import ExtractionAction
from tests.unit.policy.conftest import USER_SUBJECT


class TestExtractionRequestParsing:
    @pytest.mark.parametrize("version", ("v1", "v2"))
    def test__ListExtractedData__request_context_created(self, request_parser, version):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": f"/api/extraction/{version}/extracted-data/",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == ExtractionAction.LIST_EXTRACTED_DATA
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["document"]

    @pytest.mark.parametrize("version", ("v1", "v2"))
    def test__GetExtractedData__request_context_created(self, request_parser, version):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": f"/api/extraction/{version}/extracted-data/123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == ExtractionAction.GET_EXTRACTED_DATA
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    @pytest.mark.parametrize("version", ("v1", "v2"))
    def test__UpdateExtractedData__request_context_created(self, request_parser, version):
        request_headers = {
            "x-original-method": "PUT",
            "x-original-path": f"/api/extraction/{version}/extracted-data/123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == ExtractionAction.UPDATE_EXTRACTED_DATA
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__RemoveExtractedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/extraction/v1/extracted-data/123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == ExtractionAction.REMOVE_EXTRACTED_DATA
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__AddExtractedField__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PUT",
            "x-original-path": "/api/extraction/v1/extracted-data/123/field",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == ExtractionAction.ADD_EXTRACTED_FIELD
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__RemoveExtractedField__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/extraction/v1/extracted-data/123/fields",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == ExtractionAction.REMOVE_EXTRACTED_FIELD
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__AddTableInfo__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PUT",
            "x-original-path": "/api/extraction/v2/extracted-data/123/fields/code/table/info",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == ExtractionAction.ADD_TABLE_INFO
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__AddTableChunkedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PUT",
            "x-original-path": "/api/extraction/v2/extracted-data/123/fields/code/table/chunk",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == ExtractionAction.ADD_TABLE_CHUNKED_DATA
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__GetFieldChunk__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/extraction/v2/extracted-data/123/fields/code/chunk",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == ExtractionAction.GET_FIELD_CHUNK
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__UpdateExtractedField__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PATCH",
            "x-original-path": "/api/extraction/v2/extracted-data/123/fields/code",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "UpdateExtractedField"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]
