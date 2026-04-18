from deps_iam.domain.model import PermissionDeterminingService
from deps_iam.domain.model.policy import Principal, Resource
from deps_iam.domain.model.policy.policy_factory import ResourceBasedPolicyFactory

from .conftest import RESOURCE_STRING


def test_this_user_can_read_document(this_user_read_request_context, typicaly_identity_based_policies):
    result = PermissionDeterminingService(typicaly_identity_based_policies, this_user_read_request_context)
    assert not result.denied_resources
    assert result.has_permission


def test_this_user_can_change_document_after_review_assignment(
    this_user,
    this_user_document_affecting_request_context,
    resource_based_policy_factory: ResourceBasedPolicyFactory,
    typicaly_identity_based_policies,
):
    reviewer_policy = resource_based_policy_factory.create_reviewer_assignment(
        Resource(RESOURCE_STRING), Principal(this_user["subject"])
    )
    typicaly_identity_based_policies.update(
        {
            RESOURCE_STRING: [reviewer_policy],
        }
    )

    result = PermissionDeterminingService(
        typicaly_identity_based_policies,
        this_user_document_affecting_request_context,
    )
    assert not result.denied_resources
    assert result.has_permission


def test_not_reviewer_can_read_document(
    this_user,
    same_organisation_other_user_read_request_context,
    resource_based_policy_factory,
    typicaly_identity_based_policies,
):
    reviewer_policy = resource_based_policy_factory.create_reviewer_assignment(
        Resource(RESOURCE_STRING), Principal(this_user["subject"])
    )
    typicaly_identity_based_policies.update({RESOURCE_STRING: [reviewer_policy]})

    result = PermissionDeterminingService(
        typicaly_identity_based_policies,
        same_organisation_other_user_read_request_context,
    )

    assert not result.denied_resources
    assert result.has_permission


def test_not_reviewer_cannot_change_document(
    this_user,
    same_organisation_other_user_document_affecting_request_context,
    resource_based_policy_factory,
    typicaly_identity_based_policies,
):
    reviewer_policy = resource_based_policy_factory.create_reviewer_assignment(
        Resource(RESOURCE_STRING), Principal(this_user["subject"])
    )
    typicaly_identity_based_policies.update({RESOURCE_STRING: [reviewer_policy]})

    result = PermissionDeterminingService(
        typicaly_identity_based_policies,
        same_organisation_other_user_document_affecting_request_context,
    )

    assert result.denied_resources
    assert not result.has_permission


def test_user_from_other_organisation_hasnot_access_to_the_document(
    this_user,
    typicaly_identity_based_policies,
    resource_based_policy_factory,
    user_from_other_organisation_request_context,
):
    reviewer_policy = resource_based_policy_factory.create_reviewer_assignment(
        Resource(RESOURCE_STRING), Principal(this_user["subject"])
    )
    typicaly_identity_based_policies.update({RESOURCE_STRING: [reviewer_policy]})

    result = PermissionDeterminingService(
        typicaly_identity_based_policies,
        user_from_other_organisation_request_context,
    )

    assert result.denied_resources
    assert not result.has_permission
