from ..resource_source import ResourceSource
from .request_mapper import RawRequestContext, RequestInfo

iam_mapper: dict[RequestInfo, RawRequestContext] = {
    RequestInfo("GET", "^users/me$"): RawRequestContext("GetMe", ["user"], None, []),
    RequestInfo("GET", "^users/([^/]+)$"): RawRequestContext("GetUser", ["user"], ResourceSource.PATH, [1]),
    RequestInfo("DELETE", "^users/([^/]+)$"): RawRequestContext("RemoveUser", ["user"], ResourceSource.PATH, [1]),
    RequestInfo("PATCH", "^users/([^/]+)$"): RawRequestContext("UpdateUser", ["user"], ResourceSource.PATH, [1]),
    RequestInfo("GET", "^users$"): RawRequestContext("ListUsers", ["user"], None, []),
    RequestInfo("POST", "^users$"): RawRequestContext("CreateUser", ["user"], None, []),
    RequestInfo("GET", "^users/me/api-key$"): RawRequestContext("GetApiKey", ["user"], None, []),
    RequestInfo("DELETE", "^users/me/api-key$"): RawRequestContext("RemoveApiKey", ["user"], None, []),
    RequestInfo("POST", "^users/me/api-key/generate$"): RawRequestContext("CreateApiKey", ["user"], None, []),
    RequestInfo("GET", "^organisations$"): RawRequestContext("ListOrganisations", ["organisation"], None, []),
    RequestInfo("POST", "^organisations$"): RawRequestContext("CreateOrganisation", ["organisation"], None, []),
    RequestInfo("GET", "^organisations/([^/]+)$"): RawRequestContext(
        "GetOrganisation", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^organisations/([^/]+)$"): RawRequestContext(
        "RemoveOrganisation", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("PATCH", "^organisations/([^/]+)$"): RawRequestContext(
        "UpdateOrganisation", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("POST", "^organisations/(.*)/activate$"): RawRequestContext(
        "AddActiveOrganisation", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^organisations/(.*)/users$"): RawRequestContext(
        "ListOrganisationUsers", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^organisations/(.*)/users$"): RawRequestContext(
        "RemoveOrganisationUser", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^organisations/(.*)/invitees$"): RawRequestContext(
        "ListInvitees", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^organisations/(.*)/invitees$"): RawRequestContext(
        "RemoveInvitees", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("POST", "^organisations/(.*)/invite$"): RawRequestContext(
        "CreateInvitation", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("POST", "^organisations/(.*)/join$"): RawRequestContext(
        "CreateJoin", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("POST", "^organisations/(.*)/approve$"): RawRequestContext(
        "CreateApprove", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("DELETE", "^organisations/(.*)/approvals$"): RawRequestContext(
        "RemoveApprovals", ["organisation"], ResourceSource.PATH, [1]
    ),
    RequestInfo("GET", "^authorize$"): RawRequestContext("RunAuthorization", [], None, []),
}
