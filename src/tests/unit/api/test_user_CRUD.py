from http import HTTPStatus
from uuid import uuid4

from deps_iam import constants
from deps_iam.api.models.dtos import UserUpdateObjectModel
from deps_iam.api.models.user import UserModel
from deps_iam.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from tests.json_builders import build_expanded_user_json


class TestUserDetail:
    endpoint = constants.API_PREFIX + "/users"
    api_key = str(uuid4())

    def test_get_current_user__200(self, client, expanded_user, user_service_mock, entity_based_token):
        user_service_mock.get_expanded_user.return_value = expanded_user
        response = client.get(self.endpoint + "/me", headers={"deps-token": entity_based_token})

        assert response.status_code == HTTPStatus.OK
        assert response.json() == build_expanded_user_json(expanded_user)

    def test_get_current_user__no_token(self, client, user_service_mock):
        response = client.get(self.endpoint + "/me")

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_user__user_exists__200(self, client, user_entity, user_service_mock):
        user_service_mock.get.return_value = user_entity
        response = client.get(self.endpoint + f"/{user_entity.pk}")
        assert response.status_code == HTTPStatus.OK
        assert UserModel.model_validate(response.json()).to_domain() == user_entity

    def test_get_user__user_not_exists__404(self, client, user_service_mock):
        user_service_mock.get.side_effect = UserNotFoundError
        response = client.get(self.endpoint + "/not_existing_user_pk")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_user__user_exists__user_updated(self, client, user_factory, user_service_mock):
        old_entity, new_entity = user_factory.build_batch(2, pk="similar pk", username="email", email="email")
        user_service_mock.update.return_value = new_entity
        user_model = UserModel.model_validate(new_entity)
        response = client.patch(
            self.endpoint + f"/{old_entity.pk}", data=UserUpdateObjectModel.model_validate(new_entity).model_dump_json()
        )
        assert response.status_code == HTTPStatus.OK
        assert UserModel.model_validate(response.json()) == user_model

    def test_update_user__user_not_exists__403(self, client, user_entity, user_service_mock):
        user_service_mock.update.side_effect = UserNotFoundError
        user_model = UserModel.model_validate(user_entity)
        response = client.patch(self.endpoint + f"/{user_entity.pk}", data=user_model.model_dump_json())
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_user__user_exists__deleted(self, client, user_entity, user_service_mock):
        user_service_mock.delete.return_value = True
        response = client.delete(self.endpoint + f"/{user_entity.pk}")
        assert response.status_code == HTTPStatus.OK

    def test_delete_user__user_not_exists__404(self, client, user_service_mock):
        user_service_mock.delete.side_effect = UserNotFoundError
        response = client.delete(self.endpoint + f"/random_pk")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_create_new_user__user_not_exists__created(self, client, user_entity, user_service_mock):
        user_service_mock.add.return_value = user_entity
        response = client.post(
            self.endpoint,
            json={
                "user": {
                    "username": user_entity.username,
                    "email": user_entity.email,
                    "firstName": user_entity.first_name,
                    "lastName": user_entity.last_name,
                }
            },
        )
        assert response.status_code == HTTPStatus.CREATED

    def test_create_new_user__user_exists__conflict(self, client, user_entity, user_service_mock):
        user_service_mock.add.side_effect = UserAlreadyExistsError
        response = client.post(
            self.endpoint,
            json={
                "user": {
                    "username": user_entity.username,
                    "email": user_entity.email,
                    "firstName": user_entity.first_name,
                    "lastName": user_entity.last_name,
                }
            },
        )
        assert response.status_code == HTTPStatus.CONFLICT

    def test_create_new_user_with_api_key__user_not_exists__created(self, client, user_entity, user_service_mock):
        user_service_mock.add.return_value = user_entity
        user_service_mock.create_api_key.return_value = self.api_key

        response = client.post(
            self.endpoint,
            json={
                "user": {
                    "username": user_entity.username,
                    "email": user_entity.email,
                    "firstName": user_entity.first_name,
                    "lastName": user_entity.last_name,
                },
                "createAPIKey": True,
            },
        )

        assert response.status_code == HTTPStatus.CREATED
        assert constants.API_KEY in response.headers
        assert response.headers[constants.API_KEY] == self.api_key
