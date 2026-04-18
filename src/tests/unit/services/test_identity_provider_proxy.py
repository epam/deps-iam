import pytest
import requests_mock

from deps_iam.domain.model import UserInfo
from deps_iam.infrastructure.services.identity_provider import OpenIdIdentityProvider
from deps_iam.infrastructure.services.identity_provider.exceptions import (
    AccessTokenAuthServiceError,
)
from deps_iam.infrastructure.services.identity_provider.identity_provider import (
    IdentityResponse,
)


@pytest.fixture
def userinfo_endpoint():
    yield "https://example.com"


@pytest.fixture
def identity_provider_proxy(userinfo_endpoint):
    return OpenIdIdentityProvider(userinfo_endpoint=userinfo_endpoint)


@pytest.fixture
def userinfo_mock(userinfo_endpoint):
    with requests_mock.Mocker() as mock:
        yield mock


class TestIdentityProviderProxy:
    @staticmethod
    def _userinfo_to_response_dict(userinfo: UserInfo) -> IdentityResponse:
        return {
            "sub": userinfo.id(),
            "email": userinfo.email.value,
            "given_name": userinfo.first_name,
            "family_name": userinfo.last_name,
        }

    def test_proxy__valid_response(self, identity_provider_proxy, userinfo_mock, user_info, userinfo_endpoint):
        userinfo_mock.get(userinfo_endpoint, json=self._userinfo_to_response_dict(user_info))
        assert identity_provider_proxy.authenticate("access_token") == user_info

    def test_proxy__not_found(self, identity_provider_proxy, userinfo_mock, userinfo_endpoint):
        userinfo_mock.get(userinfo_endpoint, status_code=403)
        with pytest.raises(AccessTokenAuthServiceError):
            identity_provider_proxy.authenticate("access_token")
