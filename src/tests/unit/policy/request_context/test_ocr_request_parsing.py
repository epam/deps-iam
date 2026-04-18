import json

from tests.unit.policy.conftest import USER_SUBJECT


class TestOCRRequestParsing:
    def test__RunExtractionArea__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/ocr/v2/extract-area",
            "x-original-query": "",
        }
        body = json.dumps(
            {
                "engine": "TESSERACT",
                "language": "eng",
                "area": {"x": 1, "y": 1, "w": 1, "h": 1},
                "blobFile": "some_file.png",
                "forceOCR": False,
                "engineSettings": {},
            }
        )
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RunExtractionArea"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"blob_file": ["some_file.png"]}
        assert [r.value for r in request_context.resources] == ["blob_file"]

    def test__RunExtractionText__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/ocr/v2/extract-text",
            "x-original-query": "",
        }
        body = json.dumps({"value": "value"})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RunExtractionText"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []

    def test__ListEngines__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/ocr/v2/engines",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListEngines"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["engine"]
