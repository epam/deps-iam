import json

from tests.unit.policy.conftest import USER_SUBJECT


class TestFileStorageRequestParsing:
    def test__GetFile__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/storage/v1/file/file_path",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetFile"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"path": ["file_path"]}
        assert [r.value for r in request_context.resources] == ["path"]

    def test__CreateFile__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/storage/v1/file/file_path",
            "x-original-query": "",
        }
        body = json.dumps({"test": "test"})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "CreateFile"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"path": ["file_path"]}
        assert [r.value for r in request_context.resources] == ["path"]

    def test__RemoveFile__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/storage/v1/file/file_path",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RemoveFile"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"path": ["file_path"]}
        assert [r.value for r in request_context.resources] == ["path"]

    def test__CreateFileNoPath__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/storage/v1/file",
            "x-original-query": "",
        }
        body = json.dumps({"test": "test"})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "CreateFileNoPath"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []
