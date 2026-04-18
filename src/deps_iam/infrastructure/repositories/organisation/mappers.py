from typing import Any

from deps_iam import constants
from deps_iam.domain.dtos import OrganisationUpdate
from deps_iam.domain.dtos.organisation import EMPTY
from deps_iam.domain.entities import ApprovalRequest, Invitation, Organisation


def build_organisation_dict(entity: Organisation) -> dict[str, Any]:
    org_dict = {"name": entity.name, "customization_url": entity.customization_url}
    if entity.pk:
        org_dict["pk"] = entity.pk
    return org_dict


def build_organisation_update_dict(organisation_update: OrganisationUpdate) -> dict[str, Any]:
    update_dict = {}
    if organisation_update.name is not EMPTY:
        update_dict["name"] = organisation_update.name
    if organisation_update.customization_url is not EMPTY:
        update_dict["customization_url"] = organisation_update.customization_url
    return update_dict


def build_organisation_entity_from_dict(organisation_row: dict) -> Organisation:
    return Organisation(
        pk=organisation_row["pk"],
        name=organisation_row["name"],
        customization_url=organisation_row["customization_url"],
        is_personal=organisation_row["name"].endswith(constants.PERSONAL_ORGANISATION_POSTFIX),
    )


def build_organisation_entities_from_dict(organisation_rows: dict) -> list[Organisation]:
    return [build_organisation_entity_from_dict(org) for org in organisation_rows]


def build_invitation_from_dict(invitation_row: dict) -> Invitation:
    return Invitation(email=invitation_row["user_email"])


def build_approval_request_from_dict(approval_row: dict) -> ApprovalRequest:
    return ApprovalRequest(
        user_pk=approval_row["user_pk"],
        organisation_pk=approval_row["organisation_pk"],
        created_at=approval_row["created_at"],
    )
