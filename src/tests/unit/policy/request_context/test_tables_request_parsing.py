import json

from tests.unit.policy.conftest import USER_SUBJECT


class TestTablesRequestParsing:
    def test__RunDetectionTableStorage__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/tables/v1/storage/detect",
            "x-original-query": "",
        }
        body = json.dumps(
            {
                "ocrEngine": "TESSERACT",
                "tableDetectionEngine": "DEPS_DETECTOR",
                "language": "eng",
                "area": {"y": 1, "x": 1, "w": 1, "h": 1, "page": 1},
                "sourceId": "source_id",
                "blobFile": "some_file.png",
                "transformations": {"rotation": 90},
            }
        )
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RunDetectionTableStorage"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"blob_file": ["some_file.png"]}
        assert [r.value for r in request_context.resources] == ["blob_file"]

    def test__RunExtractionTableStorage__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/tables/v1/storage/extract",
            "x-original-query": "",
        }
        body = json.dumps(
            {
                "ocrEngine": "TESSERACT",
                "language": "eng",
                "table": {
                    "cells": [
                        {
                            "value": "string",
                            "coordinates": {"column": 0, "row": 0, "colspan": 1, "rowspan": 1, "page": 1},
                            "confidence": 1,
                            "sourceBboxCoordinates": [
                                {"sourceId": "string", "bboxes": [{"y": 1, "x": 1, "w": 1, "h": 1}]}
                            ],
                        }
                    ],
                    "rows": [{"y": 1}],
                    "columns": [{"x": 1}],
                    "coordinates": {"y": 1, "x": 1, "w": 1, "h": 1, "page": 1},
                    "sourceBboxCoordinates": {"sourceId": "string", "bboxes": [{"y": 1, "x": 1, "w": 1, "h": 1}]},
                },
                "blobFile": "some_file.png",
                "transformations": {"rotation": 90},
            }
        )
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RunExtractionTableStorage"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"blob_file": ["some_file.png"]}
        assert [r.value for r in request_context.resources] == ["blob_file"]

    def test__RunDetectionTableFile__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/tables/v1/file/detect",
            "x-original-query": "",
        }
        body = json.dumps({"test": "test"})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RunDetectionTableFile"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []

    def test__ListEngines__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/tables/v1/detection-engines",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListEngines"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["engine"]
