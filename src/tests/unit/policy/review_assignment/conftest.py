import pytest

from deps_iam.domain.model.policy import (
    DocumentAction,
    Principal,
    RequestContext,
    Resource,
)
from deps_iam.domain.model.policy.policy_factory import ResourceBasedPolicyFactory

all_document_actions = [el for el in DocumentAction.__members__.values()]
document_affecting_actions = [el for el in DocumentAction.actions_affecting_the_document()]
document_reading_actions = [el for el in DocumentAction.read_only_actions()]

RESOURCE_STRING = "drn:document:Deps_org:/admins/document/1"


@pytest.fixture
def resource_based_policy_factory():
    return ResourceBasedPolicyFactory()


@pytest.fixture
def user_from_the_same_organisation():
    return dict(
        subject="Diff user",
        groups=["Deps_organisation_name"],
        token="token",
        roles=["tester"],
        email="diff_email@epam.com",
        organisation="Deps_org",
        first_name="DiffDeps",
        last_name="DiffD",
    )


@pytest.fixture(params=(document_reading_actions))
def this_user_read_request_context(request, this_user, action_factory, resource_factory):
    resource = resource_factory(
        service="document",
        tenant=f"{this_user['organisation']}",
        something_else="/admins/document/1",
    )
    return RequestContext(
        action_factory(service="document", action=request.param, add_resource=""),
        resources=[resource],
        principal=Principal(this_user["subject"]),
        resource_data={RESOURCE_STRING: [1]},
    )


@pytest.fixture(params=(document_reading_actions))
def same_organisation_other_user_read_request_context(request, user_from_the_same_organisation, action_factory):
    resource = Resource(RESOURCE_STRING)
    return RequestContext(
        action_factory(service="document", action=request.param, add_resource=""),
        resources=[resource],
        principal=Principal(user_from_the_same_organisation["subject"]),
        resource_data={RESOURCE_STRING: [1]},
    )


@pytest.fixture(params=(document_affecting_actions))
def same_organisation_other_user_document_affecting_request_context(
    request, user_from_the_same_organisation, action_factory
):
    resource = Resource(RESOURCE_STRING)
    return RequestContext(
        action_factory(service="document", action=request.param, add_resource=""),
        resources=[resource],
        principal=Principal(user_from_the_same_organisation["subject"]),
        resource_data={RESOURCE_STRING: [1]},
    )


@pytest.fixture(params=(document_affecting_actions))
def this_user_document_affecting_request_context(request, this_user, action_factory, resource_factory):
    resource = resource_factory(
        service="document",
        tenant=f"{this_user['organisation']}",
        something_else="/admins/document/1",
    )
    return RequestContext(
        action_factory(service="document", action=request.param),
        resources=[resource],
        principal=Principal(this_user["subject"]),
        resource_data={RESOURCE_STRING: [1]},
    )


@pytest.fixture(params=(all_document_actions))
def user_from_other_organisation_request_context(
    request, other_organisation_user, resource_factory, this_user, action_factory
):
    resource = resource_factory(
        service="document",
        tenant=f"{this_user['organisation']}",
        something_else="/admins/document/1",
    )
    return RequestContext(
        action_factory(service="document", action=request.param),
        resources=[resource],
        principal=Principal(other_organisation_user["subject"]),
        resource_data={RESOURCE_STRING: [1]},
    )


@pytest.fixture
def typicaly_identity_based_policies(this_user, user_from_the_same_organisation, this_user_tenant_read_only_ibp):
    return {
        this_user["subject"]: [this_user_tenant_read_only_ibp],
        user_from_the_same_organisation["subject"]: [this_user_tenant_read_only_ibp],
    }
