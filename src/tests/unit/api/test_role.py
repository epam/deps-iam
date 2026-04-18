from http import HTTPStatus

from deps_iam import constants
from deps_iam.domain.exceptions import (
    OrganisationNotFoundError,
    PermissionNotFoundError,
    RoleAlreadyExistsError,
    RoleNotFoundError,
)


class TestRoleView:
    endpoint = f"{constants.API_PREFIX}/roles"

    def test_get__role_exists__gotten(self, client, role_service_mock, role_entity, get_role_dict):
        role_service_mock.get.return_value = role_entity
        res = client.get(f"{self.endpoint}/1")
        json_response = res.json()

        assert res.status_code == HTTPStatus.OK
        assert json_response == get_role_dict(role_entity)

    def test_get__role_not_exists__not_found(self, client, role_service_mock):
        role_service_mock.get.side_effect = RoleNotFoundError
        res = client.get(f"{self.endpoint}/1")

        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_creat__role_not_exists__created(self, client, role_service_mock, role_entity, get_role_dict):
        role_dict = get_role_dict(role_entity)
        role_service_mock.create.return_value = role_entity
        res = client.post(self.endpoint, json=role_dict)
        json_response = res.json()

        assert res.status_code == HTTPStatus.CREATED
        assert json_response == role_dict

    def test_creat__role_exists__conflict(self, client, role_service_mock, role_entity, get_role_dict):
        role_dict = get_role_dict(role_entity)
        role_service_mock.create.side_effect = RoleAlreadyExistsError
        res = client.post(self.endpoint, json=role_dict)

        assert res.status_code == HTTPStatus.CONFLICT

    def test_creat__role_not_exists__wrong_data__validation_error(self, client, role_service_mock):
        role_dict = {"nam": "test"}
        role_service_mock.create.side_effect = RoleAlreadyExistsError
        res = client.post(self.endpoint, json=role_dict)

        assert res.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_creat__organisation_not_exists__not_found(self, client, role_service_mock, role_entity, get_role_dict):
        role_dict = get_role_dict(role_entity)
        role_service_mock.create.side_effect = OrganisationNotFoundError
        res = client.post(self.endpoint, json=role_dict)

        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_creat__permission_not_exists__not_found(self, client, role_service_mock, role_entity, get_role_dict):
        role_dict = get_role_dict(role_entity)
        role_service_mock.create.side_effect = PermissionNotFoundError
        res = client.post(self.endpoint, json=role_dict)

        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_delete__role_exists__deleted(self, client, role_service_mock):
        role_service_mock.delete.return_value = None
        res = client.delete(f"{self.endpoint}/1")
        json_response = res.json()

        assert res.status_code == HTTPStatus.OK
        assert json_response is None

    def test_delete__role_not_exists__not_found(self, client, role_service_mock):
        role_service_mock.delete.side_effect = RoleNotFoundError
        res = client.delete(f"{self.endpoint}/1")

        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_update__role_exists__updated(self, client, role_service_mock, role_entity, get_role_dict):
        role_dict = get_role_dict(role_entity)
        role_service_mock.update.return_value = role_entity
        res = client.put(f"{self.endpoint}/1", json=role_dict)
        json_response = res.json()

        assert res.status_code == HTTPStatus.OK
        assert json_response == role_dict

    def test_update__role_name_exists__conflict(self, client, role_service_mock, role_entity, get_role_dict):
        role_dict = get_role_dict(role_entity)
        role_service_mock.update.side_effect = RoleAlreadyExistsError
        res = client.put(f"{self.endpoint}/1", json=role_dict)

        assert res.status_code == HTTPStatus.CONFLICT

    def test_update__role_not_exists__not_found(self, client, role_service_mock, role_entity, get_role_dict):
        role_dict = get_role_dict(role_entity)
        role_service_mock.update.side_effect = RoleNotFoundError
        res = client.put(f"{self.endpoint}/1", json=role_dict)

        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_update__permission_not_exists__not_found(self, client, role_service_mock, role_entity, get_role_dict):
        role_dict = get_role_dict(role_entity)
        role_service_mock.update.side_effect = PermissionNotFoundError
        res = client.put(f"{self.endpoint}/1", json=role_dict)

        assert res.status_code == HTTPStatus.NOT_FOUND

    def test_get_list__role_exists__gotten(self, client, role_service_mock, role_entity, get_role_dict):
        role_service_mock.get_list.return_value = [role_entity]
        res = client.get(self.endpoint)
        json_response = res.json()

        assert res.status_code == HTTPStatus.OK
        assert json_response == [get_role_dict(role_entity)]

    def test_get_list__role_not_exists__empty_list(self, client, role_service_mock):
        role_service_mock.get_list.return_value = []
        res = client.get(self.endpoint)
        json_response = res.json()

        assert res.status_code == HTTPStatus.OK
        assert json_response == []
