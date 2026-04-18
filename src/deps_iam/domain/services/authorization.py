import contextlib
import json
import uuid
from typing import Any, Dict, Mapping, Optional

from deps_iam import constants
from deps_iam.domain.entities import UserEntity
from deps_iam.domain.exceptions import IAMException, UserNotFoundError
from deps_iam.domain.services.access_token_auth_service import AccessTokenAuthService
from deps_iam.domain.services.user import UserService
from deps_iam.infrastructure.access_management.context_vars import user

from .registration import RegistrationService


class AuthorizationService:
    def __init__(
        self,
        enable_personal_org: bool,
        api_key_auth_enabled: bool,
        access_token_auth_service: AccessTokenAuthService,
        register_service: RegistrationService,
        user_service: UserService,
    ):
        self._enable_personal_org = enable_personal_org
        self._api_key_auth_enabled = api_key_auth_enabled
        self._access_token_auth_servie = access_token_auth_service
        self._register_service = register_service
        self._user_service = user_service

    def authorize(self, request_headers: Mapping[str, Any]) -> str:
        is_personal = False
        user_credentials = self._get_user_credentials(request_headers)
        user_db = self._get_user_db(user_credentials["email"])
        user_credentials["subject"] = user_db.pk if user_db else str(uuid.uuid4())
        if user_db and user_db.organisation is not None:
            user_credentials["organisation"] = user_db.organisation

        elif self._enable_personal_org:
            organisation = str(uuid.uuid4())
            is_personal = True
            user_credentials["organisation"] = organisation

        deps_token = self.create_access_token(user_credentials)
        user_credentials["deps_token"] = deps_token
        user.set(user_credentials)

        if user_db and user_db.organisation is None and user_credentials.get("organisation"):
            self._register_service.create_activate_new_user_organisation(user_credentials, user_db.pk, is_personal)

        elif not user_db:
            self._register_service.register_user(user_credentials, is_personal)
        return deps_token

    @staticmethod
    def create_access_token(data: dict) -> str:
        if not data:
            raise IAMException("No user credentials provided")
        return json.dumps(data)

    def _get_user_credentials(self, request_headers: Mapping[str, Any]) -> Dict[str, str]:
        if constants.API_KEY in request_headers and self._api_key_auth_enabled:
            user_credentials = self._get_user_credentials_from_api_key(request_headers.get(constants.API_KEY))
        else:
            user_credentials = self._get_user_credentials_from_oidc_provider(request_headers)
        return user_credentials

    def _get_user_credentials_from_api_key(self, key: str) -> Dict[str, Any]:
        user_db = self._user_service.get_user_by_api_key(key)

        organisation = user_db.pk if not user_db.organisation and self._enable_personal_org else user_db.organisation

        return {
            "subject": user_db.pk,
            "roles": [],
            "organisation": organisation,
            "groups": [organisation],
            "email": user_db.email,
            "first_name": user_db.first_name,
            "last_name": user_db.last_name,
        }

    def _get_user_credentials_from_oidc_provider(self, request_headers: Mapping[str, Any]):
        userinfo = self._access_token_auth_servie.get_userinfo(request_headers)
        return self._map_deps_token_user_credentials(userinfo)

    def _map_deps_token_user_credentials(self, decoded_token: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "email": decoded_token["email"].lower(),
            "first_name": decoded_token.get("given_name"),
            "last_name": decoded_token.get("family_name"),
            "roles": [],
            # remove after updating auth in core and services
            "groups": ["deprecated_field"],
        }

    def _get_user_db(self, email: str) -> Optional[UserEntity]:
        with contextlib.suppress(UserNotFoundError):
            return self._user_service.get_user_by_email(email)
        return None
