import json

from deps_iam.domain.model.policy.statement.action import DocumentTypeAction
from tests.unit.policy.conftest import USER_SUBJECT


class TestDocumentTypeRequestParsing:
    def test__AddUnifierPlugin__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PUT",
            "x-original-path": "/api/document-type/v1/plugins/attach-unifier",
            "x-original-query": "",
        }
        body = json.dumps({"document_type": "some_type"})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == DocumentTypeAction.ADD_UNIFIER_PLUGIN
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document_type": ["some_type"]}
        assert [r.value for r in request_context.resources] == ["document_type"]

    def test__AddExtractionPlugin__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PUT",
            "x-original-path": "/api/document-type/v1/plugins/attach-extraction",
            "x-original-query": "",
        }
        body = json.dumps({"documentType": "some_type", "plugin": {}})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == DocumentTypeAction.ADD_EXTRACTION_PLUGIN
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document_type": ["some_type"]}
        assert [r.value for r in request_context.resources] == ["document_type"]

    def test__ListTypes__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/document-type/v1/types",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == DocumentTypeAction.LIST_TYPES
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["document_type"]

    def test__AddType__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/document-type/v1/types",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == DocumentTypeAction.ADD_TYPE
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["document_type"]

    def test__GetType__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/document-type/v1/types/some_type",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == DocumentTypeAction.GET_TYPE
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document_type": ["some_type"]}
        assert [r.value for r in request_context.resources] == ["document_type"]

    def test__RemoveTemplate__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/document-type/v1/types/some_type",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == DocumentTypeAction.REMOVE_TEMPLATE
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"document_type": ["some_type"]}
        assert [r.value for r in request_context.resources] == ["document_type"]
