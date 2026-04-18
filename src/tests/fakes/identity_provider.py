from contextlib import suppress
from typing import Dict, Optional

from deps_iam.domain.model import UserInfo
from deps_iam.infrastructure.services.identity_provider.exceptions import (
    AccessTokenAuthServiceError,
)


class FakeIdentityProvider:
    def __init__(self, identities: Optional[Dict[str, UserInfo]] = None):
        self._identities = identities or {}

    def authenticate(self, access_token: str) -> UserInfo:
        with suppress(KeyError):
            return self._identities[access_token]
        raise AccessTokenAuthServiceError
