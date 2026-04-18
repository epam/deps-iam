import logging
from typing import Any, Dict, Mapping

import requests  # type: ignore

from deps_iam.domain.exceptions import AccessTokenAuthServiceError, AuthError

TOKEN_PREFIX = "Bearer "  # noqa:S105
AUTH_HEADER = "Authorization"

logger = logging.getLogger(__name__)


class AccessTokenAuthService:
    def __init__(self, userinfo_endpoint: str, verify_ssl: bool = True):
        self._userinfo_endpoint = userinfo_endpoint
        self._is_ssl_enabled = verify_ssl

    def get_userinfo(self, request_headers: Mapping[str, Any]) -> Dict[str, Any]:
        logger.info(f"Start getting userinfo from {self._userinfo_endpoint} with ssl {self._is_ssl_enabled}")
        token = self._get_token_from_header(request_headers)
        try:
            response = requests.get(
                self._userinfo_endpoint,
                headers={AUTH_HEADER: TOKEN_PREFIX + token},
                verify=self._is_ssl_enabled,
            )
            response.raise_for_status()
        except Exception as err:
            logger.error(f"Userinfo request fails with error: {err}")
            raise AccessTokenAuthServiceError
        return response.json()

    def _get_token_from_header(self, request_headers: Mapping[str, Any]) -> str:
        token = request_headers.get(AUTH_HEADER)
        if token and token.startswith(TOKEN_PREFIX):
            return token.split(" ")[1]
        raise AuthError("Request came with invalid credentials")
