from typing import Protocol

from .user_info import UserInfo

__all__ = ["IIdentityProvider"]


class IIdentityProvider(Protocol):
    def authenticate(self, access_token: str) -> UserInfo:
        pass
