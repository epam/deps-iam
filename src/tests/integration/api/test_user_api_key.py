from http import HTTPStatus
from uuid import uuid4

import pytest

from deps_iam import constants
from deps_iam.domain.exceptions import UserApiKeyNotFoundError


class TestUserApiKey:
    user_api_key_endpoint = f"{constants.API_PREFIX}/users/me/api-key"
    api_key = uuid4()

    def test_create__user_exists__ak_no_exists__created(self, client, existing_user, entity_based_token):
        response = client.post(self.user_api_key_endpoint + "/generate", headers={"deps-token": entity_based_token})

        assert response.status_code == HTTPStatus.CREATED

    def test_create__user_exists__ak_exists__new_created(
        self, client, existing_user, entity_based_token, user_api_key_repository
    ):
        api_key = user_api_key_repository.create(existing_user.pk, self.api_key)
        response = client.post(self.user_api_key_endpoint + "/generate", headers={"deps-token": entity_based_token})

        assert response.status_code == HTTPStatus.CREATED
        assert response != api_key

    def test_create__user_no_exists__ak_no_exists__404(self, client, entity_based_token):
        response = client.post(self.user_api_key_endpoint + "/generate", headers={"deps-token": entity_based_token})

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_create__without_token__401(self, client):
        response = client.post(self.user_api_key_endpoint + "/generate")

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get__ak_exists__gotten(self, client, existing_user, entity_based_token, user_api_key_repository):
        api_key = user_api_key_repository.create(existing_user.pk, self.api_key)
        response = client.get(self.user_api_key_endpoint, headers={"deps-token": entity_based_token})

        assert response.status_code == HTTPStatus.OK
        assert api_key == response.json()

    def test_get__ak_no_exists__404(self, client, existing_user, entity_based_token, user_api_key_repository):
        response = client.get(self.user_api_key_endpoint, headers={"deps-token": entity_based_token})

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get__without_token__401(self, client):
        response = client.get(self.user_api_key_endpoint)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_delete__ak_exists__deleted(self, client, existing_user, entity_based_token, user_api_key_repository):
        user_api_key_repository.create(existing_user.pk, self.api_key)
        response = client.delete(self.user_api_key_endpoint, headers={"deps-token": entity_based_token})

        assert response.status_code == HTTPStatus.NO_CONTENT
        with pytest.raises(UserApiKeyNotFoundError):
            user_api_key_repository.get(existing_user.pk)

    def test_delete__ak_no_exists__404(self, client, entity_based_token):
        response = client.delete(self.user_api_key_endpoint, headers={"deps-token": entity_based_token})

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete__without_token__401(self, client):
        response = client.delete(self.user_api_key_endpoint)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
