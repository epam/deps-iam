import logging
from typing import TypedDict

import requests

from deps_iam.domain.model import Email, EntityId, IIdentityProvider, UserInfo
from deps_iam.extras.rest_client.adapter import DEPSHTTPSAdapter

from .exceptions import AccessTokenAuthServiceError

__all__ = ["OpenIdIdentityProvider"]


class IdentityResponse(TypedDict, total=False):
    sub: str
    email: str
    name: str
    given_name: str
    family_name: str


class OpenIdIdentityProvider(IIdentityProvider):
    AUTH_HEADER = "Authorization"
    TOKEN_TYPE = "Bearer"  # noqa: S105

    def __init__(
        self,
        userinfo_endpoint: str,
        *,
        verify_ssl: bool = True,
    ):
        self._verify_ssl = verify_ssl
        self._userinfo_endpoint = userinfo_endpoint
        self._session = requests.Session()
        self._logger = logging.getLogger(self.__class__.__name__)

    def _initialize(self) -> None:
        self._mount_adapter()

    def _mount_adapter(self) -> None:
        self._session.mount(self._userinfo_endpoint, DEPSHTTPSAdapter())

    def authenticate(self, access_token: str) -> UserInfo:
        user_dict: IdentityResponse = self._get_userinfo(access_token)
        return UserInfo(
            first_name=user_dict.get("given_name"),
            last_name=user_dict.get("family_name"),
            email=Email(user_dict["email"]),
            id_=EntityId(user_dict["sub"]),
        )

    def _get_userinfo(self, access_token: str) -> IdentityResponse:
        try:
            response = self._session.get(
                self._userinfo_endpoint,
                headers={self.AUTH_HEADER: " ".join((self.TOKEN_TYPE, access_token))},
                verify=self._verify_ssl,
            )
            self._logger.debug("OpenID provider response: %s. Request: %s", response.text, response.request.__dict__)
            response.raise_for_status()
        except Exception as err:
            self._logger.error(f"Userinfo request fails with error: {err}")
            raise AccessTokenAuthServiceError
        return response.json()
