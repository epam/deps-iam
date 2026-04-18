import json
from unittest.mock import AsyncMock

import pytest
from fastapi.responses import StreamingResponse

from deps_iam.api.middleware import cache
from deps_iam.constants import API_KEY, API_PREFIX
from deps_iam.extras.auth.deps_auth import AUTH_HEADER

token_1 = "token_1"
token_2 = "token_2"

api_key_1 = "api_key_1"
api_key_2 = "api_key_2"

response_1 = {
    "subject": "user1",
    "email": "user@email.com",
    "first_name": "first_name",
    "last_name": "last_name",
    "organisation": "main_org",
}
response_2 = {
    "subject": "other_user",
    "email": "other@email.com",
    "first_name": "other_name",
    "last_name": "other_family_name",
    "organisation": "slave_org",
}


@pytest.fixture
def authorization_service(services):
    yield services.authorization()


@pytest.fixture
def cache_middleware(app):
    middleware = app.middleware_stack.app
    yield middleware
    middleware._response_cache.clear()
    middleware._credentials_cache.clear()


@pytest.fixture
def fill_in_cache(cache_middleware):
    cache_middleware._response_cache = {
        el1: el2
        for el1, el2 in zip((api_key_1, api_key_2, token_1, token_2), (response_1, response_2, response_1, response_2))
    }
    cache_middleware._credentials_cache = {
        response_1["subject"]: [api_key_1, token_1],
        response_2["subject"]: [api_key_2, token_2],
    }


@pytest.fixture
def mocked_request(mocker):
    async def fake_stream():
        for i in json.dumps({}):
            yield bytes(i, "utf-8")

    async_mock = AsyncMock(return_value=(StreamingResponse(status_code=204, content=fake_stream()), True))
    mocker.patch("deps_iam.api.middleware.cache.CacheMiddleware._make_request", side_effect=async_mock)
    return async_mock


@pytest.fixture(autouse=True)
def mock_cache_middleware(monkeypatch):
    monkeypatch.undo()


@pytest.mark.skip(reason="no way for controlling cache between workers")
class TestCachedMiddleware:
    authorize_endpoint = f"{API_PREFIX}/authorize"

    def test__api_key_in_header__added_to_cache(
        self, authorization_service, monkeypatch, mocker, client, cache_middleware
    ):
        monkeypatch.setattr(
            authorization_service,
            "authorize",
            mocker.Mock(return_value=json.dumps(response_1)),
        )

        client.get(self.authorize_endpoint, headers={API_KEY: api_key_1})

        assert api_key_1 in cache_middleware._response_cache
        assert response_1["subject"] in cache_middleware._credentials_cache

    def test__token_in_header__added_to_cache(
        self, authorization_service, monkeypatch, mocker, client, cache_middleware
    ):
        monkeypatch.setattr(
            authorization_service,
            "authorize",
            mocker.Mock(return_value=json.dumps(response_1)),
        )

        client.get(self.authorize_endpoint, headers={AUTH_HEADER: token_1})

        assert "token_1" in cache_middleware._response_cache
        assert response_1["subject"] in cache_middleware._credentials_cache

    def test__api_key_and_token_in_header__added_only_apy_key_to_cache(
        self, authorization_service, monkeypatch, mocker, client, cache_middleware
    ):
        monkeypatch.setattr(
            authorization_service,
            "authorize",
            mocker.Mock(return_value=json.dumps(response_1)),
        )

        client.get(self.authorize_endpoint, headers={AUTH_HEADER: token_1, API_KEY: api_key_1})

        assert "token_1" not in cache_middleware._response_cache
        assert response_1["subject"] in cache_middleware._credentials_cache
        assert api_key_1 in cache_middleware._response_cache

    def test__user_used_api_key_and_token__cache_has_both(
        self, authorization_service, monkeypatch, mocker, client, cache_middleware
    ):
        monkeypatch.setattr(
            authorization_service,
            "authorize",
            mocker.Mock(return_value=json.dumps(response_1)),
        )

        client.get(self.authorize_endpoint, headers={AUTH_HEADER: token_1})
        client.get(self.authorize_endpoint, headers={API_KEY: api_key_1})

        assert "token_1" in cache_middleware._response_cache
        assert api_key_1 in cache_middleware._response_cache
        assert response_1["subject"] in cache_middleware._credentials_cache
        assert len(cache_middleware._credentials_cache[response_1["subject"]]) == 2
        assert "token_1" in cache_middleware._credentials_cache[response_1["subject"]]
        assert api_key_1 in cache_middleware._credentials_cache[response_1["subject"]]

    def test__authorize_endpoint_fails__response_doesnt_add_to_cache(self, monkeypatch, client, cache_middleware):
        monkeypatch.setattr(
            cache.CacheMiddleware,
            "_make_request",
            AsyncMock(return_value=(StreamingResponse(status_code=401, content=(x for x in json.dumps({}))), False)),
        )

        client.get(self.authorize_endpoint, headers={AUTH_HEADER: token_1})
        assert len(cache_middleware._response_cache) == 0
        assert len(cache_middleware._credentials_cache) == 0

    @pytest.mark.usefixtures("mocked_request", "fill_in_cache")
    def test__delete_organisation__all_cache_cleared(self, client, cache_middleware):
        url = f"{API_PREFIX}/organisations/1"
        client.delete(url)

        assert len(cache_middleware._response_cache) == 0
        assert len(cache_middleware._credentials_cache) == 0

    @pytest.mark.usefixtures("fill_in_cache", "mocked_request")
    def test__delete_user__all_cache_cleared(self, client, cache_middleware):
        url = f"{API_PREFIX}/users/best-user"
        client.delete(url)

        assert len(cache_middleware._response_cache) == 0
        assert len(cache_middleware._credentials_cache) == 0

    @pytest.mark.usefixtures("fill_in_cache", "mocked_request")
    def test__delete_api_key__cache_current_user_cleared(self, client, cache_middleware):
        url = f"{API_PREFIX}/users/me/api-key"
        client.delete(url, headers={"deps-token": json.dumps(response_1)})

        assert token_1 not in cache_middleware._response_cache
        assert token_2 in cache_middleware._response_cache
        assert response_1["subject"] not in cache_middleware._credentials_cache
        assert response_2["subject"] in cache_middleware._credentials_cache

    @pytest.mark.usefixtures("fill_in_cache", "mocked_request")
    def test__generate_api_key__cache_current_user_cleared(self, client, cache_middleware):
        url = f"{API_PREFIX}/users/me/api-key/generate"
        client.post(url, headers={"deps-token": json.dumps(response_2)})

        assert token_1 in cache_middleware._response_cache
        assert token_2 not in cache_middleware._response_cache
        assert response_1["subject"] in cache_middleware._credentials_cache
        assert response_2["subject"] not in cache_middleware._credentials_cache

    @pytest.mark.usefixtures("fill_in_cache", "mocked_request")
    def test__activate_organisation__cache_current_user_cleared(self, client, cache_middleware):
        url = f"{API_PREFIX}/organisations/depsik-org/activate"
        client.post(url, headers={"deps-token": json.dumps(response_2)})

        assert token_1 in cache_middleware._response_cache
        assert token_2 not in cache_middleware._response_cache
        assert response_1["subject"] in cache_middleware._credentials_cache
        assert response_2["subject"] not in cache_middleware._credentials_cache

    @pytest.mark.usefixtures("fill_in_cache", "mocked_request")
    def test__join_organisation__cache_current_user_cleared(self, client, cache_middleware):
        url = f"{API_PREFIX}/organisations/deps-org/join"
        client.post(url, headers={"deps-token": json.dumps(response_1)})

        assert token_1 not in cache_middleware._response_cache
        assert token_2 in cache_middleware._response_cache
        assert response_1["subject"] not in cache_middleware._credentials_cache
        assert response_2["subject"] in cache_middleware._credentials_cache

    @pytest.mark.usefixtures("fill_in_cache")
    def test__delete_users__cache_deleted_users_cleared(self, client, cache_middleware, mocked_request):
        async def fake_stream():
            for i in json.dumps({"deletedUsers": [response_1["subject"], response_2["subject"]]}):
                yield bytes(i, "utf-8")

        mocked_request.return_value = (StreamingResponse(status_code=200, content=fake_stream()), True)
        super_puper_user = {"subject": "super-puper"}
        super_puper_user_token = "super_token"
        cache_middleware._response_cache[super_puper_user_token] = "super-puper-response"
        cache_middleware._credentials_cache[super_puper_user["subject"]] = super_puper_user_token

        url = f"{API_PREFIX}/organisations/me-org/users"
        client.request(
            "DELETE",
            url,
            headers={"deps-token": json.dumps(super_puper_user)},
            json=[response_1["subject"], response_2["subject"]],
        )

        assert token_1 not in cache_middleware._response_cache
        assert token_2 not in cache_middleware._response_cache
        assert response_1["subject"] not in cache_middleware._credentials_cache
        assert response_2["subject"] not in cache_middleware._credentials_cache
        assert super_puper_user["subject"] in cache_middleware._credentials_cache
        assert super_puper_user_token in cache_middleware._response_cache

    @pytest.mark.usefixtures(
        "set_existing_user",
        "add_user_to_organisation",
    )
    def test__unhandled_responses_doesnt_affect_on_cache(
        self, client, cache_middleware, existing_user, existing_organisation
    ):
        def check_middleware():
            assert len(cache_middleware._response_cache) == 0
            assert len(cache_middleware._credentials_cache) == 0

        headers = {
            "deps-token": json.dumps(
                {
                    "subject": existing_user.pk,
                    "token": "token",
                    "roles": [],
                    "groups": existing_user.organisation,
                    "organisation": existing_user.organisation,
                    "email": existing_user.email,
                }
            )
        }
        requests = [
            ("get", f"{API_PREFIX}/users/me", headers),
            ("get", f"{API_KEY}/users/{existing_user.pk}", headers),
            ("patch", f"{API_KEY}/users/{existing_user.pk}", headers),
            ("get", f"{API_KEY}/users", headers),
            ("post", f"{API_KEY}/users", headers),
            ("get", f"{API_KEY}/users/me/api-key", headers),
            ("get", f"{API_KEY}/organisations", headers),
            ("post", f"{API_KEY}/organisations", headers),
            ("get", f"{API_KEY}/organisations/{existing_organisation.pk}", headers),
            ("patch", f"{API_KEY}/organisations/{existing_organisation.pk}", headers),
            ("get", f"{API_KEY}/organisations/users", headers),
            ("get", f"{API_KEY}/organisations/invitees", headers),
            ("delete", f"{API_KEY}/organisations/invitees", headers),
            ("post", f"{API_KEY}/organisations/invite", headers),
            ("post", f"{API_KEY}/organisations/approve", headers),
            ("get", f"{API_KEY}/organisations/approvals", headers),
            ("delete", f"{API_KEY}/organisations/approvals", headers),
        ]
        for req in requests:
            method, url, headers = req
            client.request(method, url, headers=headers)
            check_middleware()
