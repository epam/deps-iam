import pytest

from deps_iam.domain.exceptions import (
    OrganisationNotFoundError,
    PermissionNotFoundError,
    RoleAlreadyExistsError,
    RoleNotFoundError,
)
from tests.factories import RoleEntityFactory


class TestRoleRepository:
    def test_create__role_not_exists__role_without_permissions__created(self, role_repository, existing_role):
        role_entity = existing_role(RoleEntityFactory(permissions=[]))
        create_res = role_repository.create(entity=role_entity)

        assert create_res.name == role_entity.name
        assert create_res.permissions == role_entity.permissions

    def test_create__role_not_exists__created(self, role_repository, existing_role):
        role_entity = existing_role()
        create_res = role_repository.create(entity=role_entity)

        assert create_res.name == role_entity.name
        assert create_res.permissions == role_entity.permissions

    def test_create__role_not_exists__permissions_not_exsist__not_found(self, role_repository, existing_role):
        role_entity = existing_role(permissions=False)

        with pytest.raises(PermissionNotFoundError) as err:
            role_repository.create(entity=role_entity)
        assert role_entity.permissions[0].name in str(err.value)
        assert 'is not present in table "permission"' in str(err.value)

    def test_create__role_not_exists__organisation_not_exsists__not_found(self, role_repository, existing_role):
        role_entity = existing_role(organisations=None)

        with pytest.raises(OrganisationNotFoundError) as err:
            role_repository.create(entity=role_entity)
        assert 'is not present in table "organisation"' in str(err.value)

    def test_create__role_exists__without_permissions__different_organisations__created(
        self, role_repository, existing_role
    ):
        role_entity = existing_role(RoleEntityFactory(permissions=[]))
        create_res1 = role_repository.create(entity=role_entity)
        create_res2 = role_repository.create(entity=role_entity, organisation="test")

        assert create_res1.name == role_entity.name
        assert create_res1.permissions == role_entity.permissions
        assert create_res2.name == role_entity.name
        assert create_res2.permissions == role_entity.permissions

    def test_create__role_exists__with_permissions__different_organisations__created(
        self, role_repository, existing_role
    ):
        role_entity = existing_role()
        create_res1 = role_repository.create(entity=role_entity)
        create_res2 = role_repository.create(entity=role_entity, organisation="test")

        assert create_res1.name == role_entity.name
        assert create_res1.permissions == role_entity.permissions
        assert create_res2.name == role_entity.name
        assert create_res2.permissions == role_entity.permissions

    def test_create__role_exists__one_organisation__already_exists(self, role_repository, existing_role):
        role_entity = existing_role()
        role_repository.create(entity=role_entity)

        with pytest.raises(RoleAlreadyExistsError) as err:
            role_repository.create(entity=role_entity)
        assert str(err.value) == f"Role '{role_entity.name}' already exists"

    def test_get__role_not_exists__not_found(self, role_repository):
        role_pk = 0

        with pytest.raises(RoleNotFoundError) as err:
            role_repository.get(pk=role_pk)
        assert str(err.value) == f"Role with pk '{role_pk}' doesn't exist"

    def test_get__role_exists__gotten(self, role_repository, existing_role):
        role_entity = existing_role()
        create_res = role_repository.create(entity=role_entity)
        get_res = role_repository.get(pk=create_res.pk)

        assert create_res.name == get_res.name
        assert create_res.permissions == get_res.permissions

    def test_delete__role_not_exists__not_found(self, role_repository):
        role_pk = 0

        with pytest.raises(RoleNotFoundError) as err:
            role_repository.delete(pk=role_pk)
        assert str(err.value) == f"Role with pk '{role_pk}' doesn't exist"

    def test_delete__role_exists__deleted(self, role_repository, existing_role):
        role_entity = existing_role()
        create_res = role_repository.create(entity=role_entity)
        role_repository.delete(pk=create_res.pk)

        with pytest.raises(RoleNotFoundError) as err:
            role_repository.get(pk=create_res.pk)
        assert str(err.value) == f"Role with pk '{create_res.pk}' doesn't exist"

    def test_update__role_not_exists__not_found(self, role_repository, role_entity):
        role_pk = 0

        with pytest.raises(RoleNotFoundError) as err:
            role_repository.update(pk=role_pk, entity=role_entity)
        assert str(err.value) == f"Role with pk '{role_pk}' doesn't exist"

    def test_update__role_exists__add_permissions__updated(self, role_repository, existing_role):
        role_entity1 = existing_role(RoleEntityFactory(permissions=[]))
        create_res = role_repository.create(entity=role_entity1)
        role_entity2 = existing_role(RoleEntityFactory(pk=create_res.pk), organisations=None)
        update_res = role_repository.update(pk=create_res.pk, entity=role_entity2)
        get_res = role_repository.get(pk=create_res.pk)

        assert create_res.name != update_res.name
        assert create_res.permissions != update_res.permissions
        assert get_res.name == update_res.name
        assert get_res.permissions == update_res.permissions

    def test_update__role_exists__wrong_permissions__not_found(self, role_repository, existing_role):
        role_entity1 = existing_role(RoleEntityFactory(permissions=[]))
        create_res = role_repository.create(entity=role_entity1)
        role_entity2 = existing_role(RoleEntityFactory(pk=create_res.pk), permissions=False, organisations=None)

        with pytest.raises(PermissionNotFoundError) as err:
            role_repository.update(pk=create_res.pk, entity=role_entity2)
        assert role_entity2.permissions[0].name in str(err.value)
        assert 'is not present in table "permission"' in str(err.value)

    def test_update__role_exists__remove_permissions__updated(self, role_repository, existing_role):
        role_entity1 = existing_role(RoleEntityFactory())
        create_res = role_repository.create(entity=role_entity1)
        role_entity2 = existing_role(RoleEntityFactory(pk=create_res.pk, permissions=[]), organisations=None)
        update_res = role_repository.update(pk=create_res.pk, entity=role_entity2)
        get_res = role_repository.get(pk=create_res.pk)

        assert create_res.name != update_res.name
        assert create_res.permissions != update_res.permissions
        assert get_res.name == update_res.name
        assert get_res.permissions == update_res.permissions

    def test_update__roles_exist__name_used__already_exists(self, role_repository, existing_role):
        role_entity1 = existing_role(RoleEntityFactory())
        role_entity2 = existing_role(RoleEntityFactory(), organisations=None)
        role_repository.create(entity=role_entity1)
        create_res2 = role_repository.create(entity=role_entity2)

        with pytest.raises(RoleAlreadyExistsError) as err:
            role_repository.update(pk=create_res2.pk, entity=role_entity1)
        assert str(err.value) == f"Role '{role_entity1.name}' already exists"

    def test_get_list__roles_not_exist__empty_list(self, role_repository):
        get_res = role_repository.get_list()

        assert get_res == []

    def test_get_list_for_organisation__roles_exist_for_diff_organisations__gotten(
        self, role_repository, existing_role
    ):
        creat_res1 = role_repository.create(entity=existing_role(RoleEntityFactory()), organisation="test")
        creat_res2 = role_repository.create(
            entity=existing_role(RoleEntityFactory(), organisations=None), organisation="test1"
        )
        creat_res3 = role_repository.create(entity=existing_role(RoleEntityFactory(), organisations=None))
        get_res = role_repository.get_list()

        assert len(get_res) == 3
        assert creat_res1 in get_res
        assert creat_res2 in get_res
        assert creat_res3 in get_res
