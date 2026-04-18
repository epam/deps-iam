import json

from tests.unit.policy.conftest import USER_SUBJECT


class TestIamRequestParsing:
    def test__GetMe__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/iam/v1/users/me",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetMe"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["user"]

    def test__GetUser__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/iam/v1/users/user123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetUser"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"user": ["user123"]}
        assert [r.value for r in request_context.resources] == ["user"]

    def test__RemoveUser__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/iam/v1/users/user123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RemoveUser"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"user": ["user123"]}
        assert [r.value for r in request_context.resources] == ["user"]

    def test__UpdateUser__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PATCH",
            "x-original-path": "/api/iam/v1/users/user123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "UpdateUser"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"user": ["user123"]}
        assert [r.value for r in request_context.resources] == ["user"]

    def test__ListUsers__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/iam/v1/users",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListUsers"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["user"]

    def test__CreateUser__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/iam/v1/users",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "CreateUser"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["user"]

    def test__GetApiKey__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/iam/v1/users/me/api-key",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetApiKey"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["user"]

    def test__RemoveApiKey__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/iam/v1/users/me/api-key",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RemoveApiKey"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["user"]

    def test__CreateApiKey__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/iam/v1/users/me/api-key/generate",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "CreateApiKey"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["user"]

    def test__ListOrganisations__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/iam/v1/organisations",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListOrganisations"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__CreateOrganisation__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/iam/v1/organisations",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "CreateOrganisation"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__GetOrganisation__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/iam/v1/organisations/org123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "GetOrganisation"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__RemoveOrganisation__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/iam/v1/organisations/org123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RemoveOrganisation"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__UpdateOrganisation__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "PATCH",
            "x-original-path": "/api/iam/v1/organisations/org123",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "UpdateOrganisation"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__AddActiveOrganisation__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/iam/v1/organisations/org123/activate",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "AddActiveOrganisation"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__ListOrganisationUsers__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/iam/v1/organisations/org123/users",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListOrganisationUsers"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__RemoveOrganisationUser__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/iam/v1/organisations/org123/users",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RemoveOrganisationUser"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__ListInvitees__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/iam/v1/organisations/org123/invitees",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "ListInvitees"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__RemoveInvitees__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/iam/v1/organisations/org123/invitees",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RemoveInvitees"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__CreateInvitation__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/iam/v1/organisations/org123/invite",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "CreateInvitation"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__CreateJoin__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/iam/v1/organisations/org123/join",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "CreateJoin"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__CreateApprove__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "POST",
            "x-original-path": "/api/iam/v1/organisations/org123/approve",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "CreateApprove"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__RemoveApprovals__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "DELETE",
            "x-original-path": "/api/iam/v1/organisations/org123/approvals",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RemoveApprovals"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {"organisation": ["org123"]}
        assert [r.value for r in request_context.resources] == ["organisation"]

    def test__RunAuthorization__request_context_created(self, request_parser):
        request_headers = {
            "x-original-method": "GET",
            "x-original-path": "/api/iam/v1/authorize",
            "x-original-query": "",
        }
        body = json.dumps({})
        request_context = request_parser.parse_request(request_headers, body, USER_SUBJECT)

        assert request_context.action.value == "RunAuthorization"
        assert request_context.principal.value == USER_SUBJECT
        assert request_context.resource_data == {}
        assert [r.value for r in request_context.resources] == []
