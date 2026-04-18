import json

from tests.unit.policy.conftest import USER_SUBJECT


class TestParsedDataRequestParsing:
    def test__GetParsedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/parsed-data/v1/parsed-data/123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetParsedData"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__RemoveParsedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/parsed-data/v1/parsed-data/123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RemoveParsedData"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__UpdateParsedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PUT",
            "x-original-path": "/api/parsed-data/v1/parsed-data",
            "x-original-query": "",
        }
        body = json.dumps(
            {"documentId": 123, "items": [{"type": "doc_type", "data": ["string"], "sourceId": "string"}]}
        )
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "UpdateParsedData"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": [123]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__UpdateParsedDataItem__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PUT",
            "x-original-path": "/api/parsed-data/v1/parsed-data-item",
            "x-original-query": "",
        }
        body = json.dumps({"type": "doc_type", "data": ["string"], "sourceId": "string", "documentId": 123})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "UpdateParsedDataItem"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": [123]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__GetSourceParsedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/parsed-data/v1/parsed-data/sources/source_id",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetSourceParsedData"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__RemoveSourceParsedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/parsed-data/v1/parsed-data/sources/source_id",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RemoveSourceParsedData"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["document"]
