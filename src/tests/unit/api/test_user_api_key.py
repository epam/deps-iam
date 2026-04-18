from http import HTTPStatus
from unittest.mock import patch
from uuid import uuid4

import pytest

from deps_iam import constants
from deps_iam.domain.exceptions import UserApiKeyNotFoundError
from deps_iam.extras.auth.deps_auth import DepsAuthService
from deps_iam.extras.auth.exceptions import EmptyAuthorizationHeader


@pytest.fixture
def deps_auth_authorize_mock():
    with patch.object(DepsAuthService, "authorize") as authorize:
        yield authorize


class TestUserApiKeyView:
    endpoint = f"{constants.API_PREFIX}/users/me/api-key"
    api_key = str(uuid4())
    user_pk = str(uuid4())

    def test_get__ak_exists__gotten(self, client, deps_auth_authorize_mock, user_service_mock):
        deps_auth_authorize_mock.return_value = {"subject": self.user_pk}
        user_service_mock.get_api_key.return_value = self.api_key
        res = client.get(self.endpoint)
        json_response = res.json()

        assert res.status_code == HTTPStatus.OK
        assert json_response == self.api_key
        deps_auth_authorize_mock.assert_called_once()
        user_service_mock.get_api_key.assert_called_once_with(self.user_pk)

    def test_get__wrong_user__401(self, client, deps_auth_authorize_mock, user_service_mock):
        deps_auth_authorize_mock.side_effect = EmptyAuthorizationHeader
        res = client.get(self.endpoint)

        assert res.status_code == HTTPStatus.UNAUTHORIZED
        deps_auth_authorize_mock.assert_called_once()
        user_service_mock.get_api_key.assert_not_called()

    def test_get__ak_no_exists__404(self, client, deps_auth_authorize_mock, user_service_mock):
        deps_auth_authorize_mock.return_value = {"subject": self.user_pk}
        user_service_mock.get_api_key.side_effect = UserApiKeyNotFoundError
        res = client.get(self.endpoint)

        assert res.status_code == HTTPStatus.NOT_FOUND
        deps_auth_authorize_mock.assert_called_once()
        user_service_mock.get_api_key.assert_called_once_with(self.user_pk)

    def test_post__created(self, client, deps_auth_authorize_mock, user_service_mock):
        deps_auth_authorize_mock.return_value = {"subject": self.user_pk}
        user_service_mock.create_api_key.return_value = self.api_key
        res = client.post(f"{self.endpoint}/generate")
        json_response = res.json()

        assert res.status_code == HTTPStatus.CREATED
        assert json_response == self.api_key
        deps_auth_authorize_mock.assert_called_once()
        user_service_mock.create_api_key.assert_called_once_with(self.user_pk)

    def test_post__wrong_user__401(self, client, deps_auth_authorize_mock, user_service_mock):
        deps_auth_authorize_mock.side_effect = EmptyAuthorizationHeader
        res = client.post(f"{self.endpoint}/generate")

        assert res.status_code == HTTPStatus.UNAUTHORIZED
        deps_auth_authorize_mock.assert_called_once()
        user_service_mock.create_api_key.assert_not_called()

    def test_delete__ak_exists__no_errors(self, client, deps_auth_authorize_mock, user_service_mock):
        deps_auth_authorize_mock.return_value = {"subject": self.user_pk}
        user_service_mock.delete_api_key.return_value = None
        res = client.delete(self.endpoint)

        assert res.status_code == HTTPStatus.NO_CONTENT
        deps_auth_authorize_mock.assert_called_once()
        user_service_mock.delete_api_key.assert_called_once_with(self.user_pk)

    def test_delete__wrong_user__401(self, client, deps_auth_authorize_mock, user_service_mock):
        deps_auth_authorize_mock.side_effect = EmptyAuthorizationHeader
        res = client.delete(self.endpoint)

        assert res.status_code == HTTPStatus.UNAUTHORIZED
        deps_auth_authorize_mock.assert_called_once()
        user_service_mock.delete_api_key.assert_not_called()

    def test_delete__ak_no_exists__404(self, client, deps_auth_authorize_mock, user_service_mock):
        deps_auth_authorize_mock.return_value = {"subject": self.user_pk}
        user_service_mock.delete_api_key.side_effect = UserApiKeyNotFoundError
        res = client.delete(self.endpoint)

        assert res.status_code == HTTPStatus.NOT_FOUND
        deps_auth_authorize_mock.assert_called_once()
        user_service_mock.delete_api_key.assert_called_once_with(self.user_pk)
