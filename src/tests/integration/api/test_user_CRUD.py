from dataclasses import asdict
from http import HTTPStatus

from deps_iam import constants
from deps_iam.api.models.dtos import UserUpdateObjectModel
from deps_iam.api.models.user import UserModel
from deps_iam.domain.dtos import ExpandedUser
from tests.json_builders import build_expanded_user_json


class TestUserDetail:
    user_endpoint = constants.API_PREFIX + "/users"

    def test_get_current_user__200(self, user_repository, client, user_entity, entity_based_token, config):
        entity = user_repository.add(user_entity)
        response = client.get(self.user_endpoint + "/me", headers={"deps-token": entity_based_token})

        assert response.status_code == HTTPStatus.OK
        assert response.json() == build_expanded_user_json(
            ExpandedUser(**asdict(entity), default_customization_url=config.default_customization_url())
        )

    def test_get_user__user_exists__200(self, user_repository, client, user_entity):
        entity = user_repository.add(user_entity)
        response = client.get(self.user_endpoint + f"/{entity.pk}")
        assert response.status_code == HTTPStatus.OK
        assert UserModel.model_validate(response.json()).to_domain() == entity

    def test_get_user__user_not_exists__404(self, client):
        response = client.get(self.user_endpoint + "/not_existing_user_pk")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_user__user_exists__user_updated(self, user_repository, client, user_factory):
        old_entity, new_entity = user_factory.build_batch(2, pk="similar pk", username="email", email="email")
        user_repository.add(old_entity)
        new_entity_update_object = UserUpdateObjectModel.model_validate(new_entity)
        response = client.patch(
            self.user_endpoint + f"/{old_entity.pk}", data=new_entity_update_object.model_dump_json()
        )
        assert response.status_code == HTTPStatus.OK
        response_object = UserModel.model_validate(response.json()).to_domain()
        # creation date is not allowed to modify
        assert old_entity.created_at == response_object.created_at != new_entity.created_at
        response_object.created_at = new_entity.created_at
        assert response_object == new_entity

    def test_update_user__user_exists_send_full_entity__certain_fields_updated(
        self, user_repository, client, user_factory
    ):
        old_entity, new_entity = user_factory.build_batch(2)
        user_repository.add(old_entity)
        request_data = UserModel.model_validate(new_entity).model_dump_json()
        response = client.patch(self.user_endpoint + f"/{old_entity.pk}", data=request_data)
        assert response.status_code == HTTPStatus.OK
        response_object = UserModel.model_validate(response.json()).to_domain()
        assert response_object.pk == old_entity.pk != new_entity.pk
        assert response_object.created_at == old_entity.created_at != new_entity.created_at
        response_object.pk = new_entity.pk
        response_object.created_at = new_entity.created_at
        response_object.username = new_entity.username
        response_object.email = new_entity.email
        assert response_object == new_entity

    def test_update_user__user_not_exists__404(self, client, user_entity):
        user_model = UserModel.model_validate(user_entity)
        response = client.patch(self.user_endpoint + f"/{user_entity.pk}", data=user_model.model_dump_json())
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_user__empty_data__422(self, client, user_entity):
        response = client.patch(self.user_endpoint + f"/{user_entity.pk}", data="{}")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_delete_user__user_exists__deleted(self, user_repository, client, user_entity):
        entity = user_repository.add(user_entity)
        response = client.delete(self.user_endpoint + f"/{entity.pk}")
        assert response.status_code == HTTPStatus.OK

    def test_delete_user__user_not_exists__404(self, client):
        response = client.delete(self.user_endpoint + "/random_pk")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_create_user_with_same_email_after_delete__created(
        self,
        user_repository,
        client,
        user_entity,
    ):
        entity = user_repository.add(user_entity)

        deleted_response = client.delete(self.user_endpoint + f"/{entity.pk}")
        assert deleted_response.status_code == HTTPStatus.OK

        created_response = client.post(
            self.user_endpoint,
            json={
                "user": {
                    "email": entity.email,
                    "username": entity.username,
                    "firstName": entity.first_name,
                    "lastName": entity.last_name,
                    "organisation": entity.organisation,
                }
            },
        )
        created_response_json = created_response.json()

        assert created_response.status_code == HTTPStatus.CREATED
        assert created_response_json["pk"] != user_entity.pk
        assert created_response_json["username"] == user_entity.username
        assert created_response_json["email"] == user_entity.email
        assert created_response_json["firstName"] == user_entity.first_name
        assert created_response_json["lastName"] == user_entity.last_name
