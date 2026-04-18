from typing import Any, Dict, Mapping, Optional

from deps_iam.domain.dtos import ExpandedUser, UserUpdateObject
from deps_iam.domain.entities import Organisation
from deps_iam.domain.entities.user import UserEntity
from deps_iam.infrastructure.repositories.organisation.mappers import (
    build_organisation_entity_from_dict,
)


def _get_common_user_fields(user_dict: Mapping) -> Dict[str, Any]:
    return {
        "pk": user_dict["pk"],
        "created_at": user_dict["created_at"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "first_name": user_dict["first_name"],
        "last_name": user_dict["last_name"],
    }


def build_user_from_dict(user_dict: Mapping) -> UserEntity:
    return UserEntity(
        **_get_common_user_fields(user_dict),
        organisation=user_dict["organisation"],
    )


def build_dict_from_user(user: UserEntity) -> Dict[str, Any]:
    return {
        "pk": user.pk,
        "created_at": user.created_at,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "organisation": user.organisation,
    }


def build_dict_from_user_update_object(update_object: UserUpdateObject) -> Dict[str, Any]:
    dict_with_nones = {
        "first_name": update_object.first_name,
        "last_name": update_object.last_name,
        "organisation": update_object.organisation,
    }
    return {k: v for k, v in dict_with_nones.items() if v is not None}


def _map_organisation_fields(user_dict: Mapping) -> Dict[str, Any]:
    mapped_dict = {}
    for key, value in user_dict.items():
        if key.startswith("org_"):
            mapped_dict[key.replace("org_", "", 1)] = value
    return mapped_dict


def _build_organisation(user_dict: Mapping) -> Optional[Organisation]:
    org_fields = _map_organisation_fields(user_dict)
    if all((value is None for value in org_fields.values())):
        return None
    return build_organisation_entity_from_dict(org_fields)


def build_expanded_user_from_dict(user_dict: Mapping) -> ExpandedUser:
    return ExpandedUser(**_get_common_user_fields(user_dict), organisation=_build_organisation(user_dict))
