import json

from deps_iam.domain.model.policy.statement.action import UnifierAction
from tests.unit.policy.conftest import USER_SUBJECT


class TestUnifierRequestParsing:
    def test__GetUnifiedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/unifier/v1/unified_data/123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == UnifierAction.GET_UNIFIED_DATA
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__UpdateUnifiedData__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PUT",
            "x-original-path": "/api/unifier/v1/unified_data/upsert-data",
            "x-original-query": "",
        }
        body = json.dumps({"documentId": 123, "elements": []})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == UnifierAction.UPDATE_UNIFIED_DATA
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": [123]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__RunTransformations__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PATCH",
            "x-original-path": "/api/unifier/v1/unified_data/123/transformations",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == UnifierAction.RUN_TRANSFORMATIONS
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__ListCells__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/unifier/v1/unified_data/123/tables/5/cells",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == UnifierAction.LIST_CELLS
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["123"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__AddCells__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/unifier/v1/cells",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == UnifierAction.ADD_CELLS
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["document"]
