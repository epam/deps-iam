import json

from tests.unit.policy.conftest import USER_SUBJECT


class TestValidationRequestParsing:
    def test__RunValidationDocument__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/validation/v1/document-validation",
            "x-original-query": "documentPk=11",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RunValidationDocument"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["11"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__RunValidationFields__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/validation/v1/fields",
            "x-original-query": "",
        }
        body = json.dumps(
            [
                {
                    "data": {"value": "some_value"},
                    "document_id": 11,
                    "document_type_code": "document_type_code",
                    "field_code": "field_code",
                },
                {
                    "data": {"value": "some_value"},
                    "document_id": 22,
                    "document_type_code": "document_type_code",
                    "field_code": "field_code",
                },
            ]
        )
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RunValidationFields"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": [11, 22]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__ListFields__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/validation/v1/fields/business",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListFields"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []

    def test__CreateFields__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/validation/v1/fields/business",
            "x-original-query": "",
        }
        body = json.dumps({"value": "value"})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "CreateFields"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []

    def test__RemoveField__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/validation/v1/fields/business/doc_type_code/field_code",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RemoveField"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []

    def test__GetField__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/validation/v1/fields/business/doc_type_code/field_code",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetField"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []

    def test__UpdateField__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PATCH",
            "x-original-path": "/api/validation/v1/fields/business/doc_type_code/field_code",
            "x-original-query": "",
        }
        body = json.dumps({"value": "value"})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "UpdateField"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []

    def test__GetValidationResults__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/validation/v1/results/11",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetValidationResults"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document": ["11"]}
        assert [r.value for r in request_context.resources] == ["document"]

    def test__ListRules__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/validation/v1/rules",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListRules"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []

    def test__CreateRule__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/validation/v1/rules",
            "x-original-query": "",
        }
        body = json.dumps({"value": "value"})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "CreateRule"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []

    def test__RemoveRule__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/validation/v1/rules/123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RemoveRule"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []

    def test__GetRule__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/validation/v1/rules/3",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetRule"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []

    def test__UpdateRule__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PATCH",
            "x-original-path": "/api/validation/v1/rules/3",
            "x-original-query": "",
        }
        body = json.dumps({"value": "value"})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "UpdateRule"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []
