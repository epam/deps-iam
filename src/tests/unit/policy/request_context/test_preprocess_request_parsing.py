import json

from tests.unit.policy.conftest import USER_SUBJECT


class TestPreprocessRequestParsing:
    def test__GetPreprocessedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/preprocess/v1/preprocessed-data/111",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetPreprocessedData"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["111"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__GetPreprocessedTableData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/preprocess/v1/preprocessed-table-data/11/5",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetPreprocessedTableData"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["11"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__GetUnifiedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/preprocess/v1/unified_data/11",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetUnifiedData"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["11"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__UpdateUnifiedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PUT",
            "x-original-path": "/api/preprocess/v1/unified_data/upsert-data",
            "x-original-query": "",
        }
        body = json.dumps(
            {
                "documentId": 111,
                "elements": [
                    {
                        "id": "1",
                        "page": 1,
                        "maxRow": 2,
                        "maxColumn": 2,
                        "coordinates": {"x": 1, "y": 1, "w": 1, "h": 1},
                        "name": "name",
                    }
                ],
            }
        )
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "UpdateUnifiedData"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": [111]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__UpdateUnifiedDataElement__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PATCH",
            "x-original-path": "/api/preprocess/v1/unified_data/11/add-element",
            "x-original-query": "",
        }
        body = json.dumps({"value": "value"})

        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "UpdateUnifiedDataElement"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["11"]}
        assert [r.value for r in request_context.resources] == ["document"]
