from http import HTTPStatus

from deps_iam import constants
from tests.factories import RoleEntityFactory

ROOT_ENDPOINT = f"{constants.API_PREFIX}/roles"


class TestRolesAPI:
    def test_create_role__no_role__without_permissions__created(self, client, existing_role, get_role_dict):
        role_entity_dict = get_role_dict(existing_role(RoleEntityFactory(permissions=[])))
        res = client.post(ROOT_ENDPOINT, json=role_entity_dict)
        json_response = res.json()

        assert res.status_code == HTTPStatus.CREATED
        assert json_response["pk"]
        assert json_response["name"] == role_entity_dict["name"]
        assert json_response["permissions"] == []

    def test_create_role__no_role__with_permissions__created(self, client, existing_role, get_role_dict):
        role_entity_dict = get_role_dict(existing_role())
        res = client.post(ROOT_ENDPOINT, json=role_entity_dict)
        json_response = res.json()

        assert res.status_code == HTTPStatus.CREATED
        assert json_response["pk"]
        assert json_response["name"] == role_entity_dict["name"]
        assert json_response["permissions"] == role_entity_dict["permissions"]

    def test_create_role__no_role__with_wrong_permissions__not_found(self, client, existing_role, get_role_dict):
        role_entity_dict = get_role_dict(existing_role(permissions=False))
        res = client.post(ROOT_ENDPOINT, json=role_entity_dict)
        json_response = res.json()

        assert res.status_code == HTTPStatus.NOT_FOUND
        assert json_response["code"] == "permission_not_found_error"
        assert 'is not present in table "permission"' in json_response["message"]

    def test_create_role__role_exists__one_organisation__conflict(
        self, client, existing_role, role_repository, get_role_dict
    ):
        role_entity = existing_role()
        role_repository.create(entity=role_entity)
        res = client.post(ROOT_ENDPOINT, json=get_role_dict(role_entity))
        json_response = res.json()

        assert res.status_code == HTTPStatus.CONFLICT
        assert json_response["code"] == "role_already_exists"
        assert json_response["message"] == f"Role '{role_entity.name}' already exists"

    def test_create_role__role_exists__different_organisations__created(
        self, client, existing_role, role_repository, get_role_dict
    ):
        role_entity = existing_role()
        role_entity_dict = get_role_dict(role_entity)
        role_repository.create(entity=role_entity, organisation="test")
        res = client.post(ROOT_ENDPOINT, json=role_entity_dict)
        json_response = res.json()

        assert res.status_code == HTTPStatus.CREATED
        assert json_response["name"] == role_entity_dict["name"]
        assert json_response["permissions"] == role_entity_dict["permissions"]

    def test_get_roles__no_roles__empty_list(self, client):
        res = client.get(ROOT_ENDPOINT)
        json_response = res.json()

        assert res.status_code == HTTPStatus.OK
        assert json_response == []

    def test_get_roles__roles_exist__one_organisation__all_gotten(
        self, client, role_repository, existing_role, get_role_dict
    ):
        role1 = role_repository.create(entity=existing_role(RoleEntityFactory()))
        role2 = role_repository.create(entity=existing_role(RoleEntityFactory(), organisations=None))
        res = client.get(ROOT_ENDPOINT)
        json_response = res.json()

        assert res.status_code == HTTPStatus.OK
        assert len(json_response) == 2
        assert get_role_dict(role1) in json_response
        assert get_role_dict(role2) in json_response

    def test_get_roles__roles_exist__diff_organisations__all_gotten(
        self, client, role_repository, existing_role, get_role_dict
    ):
        role1 = role_repository.create(entity=existing_role(RoleEntityFactory()), organisation="test")
        role2 = role_repository.create(entity=existing_role(RoleEntityFactory(), organisations=None))
        res = client.get(ROOT_ENDPOINT)
        json_response = res.json()

        assert res.status_code == HTTPStatus.OK
        assert len(json_response) == 2
        assert get_role_dict(role1) in json_response
        assert get_role_dict(role2) in json_response

    def test_get_role__role_exists__gotten(self, client, role_repository, existing_role, get_role_dict):
        role = role_repository.create(entity=existing_role())
        res = client.get(f"{ROOT_ENDPOINT}/{role.pk}")
        json_response = res.json()

        assert res.status_code == HTTPStatus.OK
        assert get_role_dict(role) == json_response

    def test_get_role__role_not_exists__not_found(self, client):
        role_pk = 0
        res = client.get(f"{ROOT_ENDPOINT}/{role_pk}")
        json_response = res.json()

        assert res.status_code == HTTPStatus.NOT_FOUND
        assert json_response["code"] == "role_not_found"
        assert json_response["message"] == f"Role with pk '{role_pk}' doesn't exist"

    def test_update_role__role_exists__add_permissions__updated(
        self, client, role_repository, existing_role, get_role_dict
    ):
        role1 = role_repository.create(entity=existing_role(RoleEntityFactory(permissions=[])))
        role2 = existing_role(RoleEntityFactory(pk=role1.pk), organisations=None)
        res_put = client.put(f"{ROOT_ENDPOINT}/{role1.pk}", json=get_role_dict(role2))
        res_get = client.get(f"{ROOT_ENDPOINT}/{role1.pk}")
        json_response = res_put.json()
        json_response2 = res_get.json()

        assert res_put.status_code == HTTPStatus.OK
        assert get_role_dict(role2) == json_response
        assert json_response == json_response2

    def test_update_role__role_exists__remove_permission__updated(
        self, client, role_repository, existing_role, get_role_dict
    ):
        role1 = role_repository.create(entity=existing_role(RoleEntityFactory()))
        role2 = existing_role(RoleEntityFactory(pk=role1.pk, permissions=[]), organisations=None)
        res_put = client.put(f"{ROOT_ENDPOINT}/{role1.pk}", json=get_role_dict(role2))
        res_get = client.get(f"{ROOT_ENDPOINT}/{role1.pk}")
        json_response = res_put.json()
        json_response2 = res_get.json()

        assert res_put.status_code == HTTPStatus.OK
        assert get_role_dict(role2) == json_response
        assert json_response == json_response2

    def test_update_role__role_not_exists__not_found(self, client, role_repository, existing_role, get_role_dict):
        role = existing_role(RoleEntityFactory())
        res = client.put(f"{ROOT_ENDPOINT}/{role.pk}", json=get_role_dict(role))
        json_response = res.json()

        assert res.status_code == HTTPStatus.NOT_FOUND
        assert json_response["code"] == "role_not_found"
        assert json_response["message"] == f"Role with pk '{role.pk}' doesn't exist"

    def test_update_role__role_exists__same_name_with_another_role__conflict(
        self, client, role_repository, existing_role, get_role_dict
    ):
        role1 = role_repository.create(entity=existing_role(RoleEntityFactory()))
        role2 = role_repository.create(entity=existing_role(RoleEntityFactory(), organisations=None))
        role3 = RoleEntityFactory(name=role1.name)
        res = client.put(f"{ROOT_ENDPOINT}/{role2.pk}", json=get_role_dict(role3))
        json_response = res.json()

        assert res.status_code == HTTPStatus.CONFLICT
        assert json_response["code"] == "role_already_exists"
        assert json_response["message"] == f"Role '{role1.name}' already exists"

    def test_delete_role__role_not_exists__not_found(self, client):
        role_pk = 0
        res = client.delete(f"{ROOT_ENDPOINT}/{role_pk}")
        json_response = res.json()

        assert res.status_code == HTTPStatus.NOT_FOUND
        assert json_response["code"] == "role_not_found"
        assert json_response["message"] == f"Role with pk '{role_pk}' doesn't exist"

    def test_delete_role__roles_exist__deleted(self, client, role_repository, existing_role, get_role_dict):
        role1 = role_repository.create(entity=existing_role(RoleEntityFactory()))
        role2 = role_repository.create(entity=existing_role(RoleEntityFactory(), organisations=None))
        res_del = client.delete(f"{ROOT_ENDPOINT}/{role1.pk}")
        get_all = client.get(ROOT_ENDPOINT)
        json_get_all = get_all.json()

        assert res_del.status_code == HTTPStatus.OK
        assert len(json_get_all) == 1
        assert get_role_dict(role1) not in json_get_all
        assert get_role_dict(role2) in json_get_all
