import pytest

from deps_iam.domain.exceptions import RoleAlreadyExistsError, RoleNotFoundError


@pytest.fixture
def role_service(services):
    services.role.reset_override()
    return services.role


class TestRoleService:
    def test_create__entity_returned(self, repositories, role_entity, role_service):
        repositories.role().create.return_value = role_entity
        role = role_service().create(role_entity)

        assert role is role_entity
        repositories.role().create.assert_called_once_with(role_entity)

    def test_create__already_exists_error(self, repositories, role_entity, role_service):
        repositories.role().create.side_effect = RoleAlreadyExistsError

        with pytest.raises(RoleAlreadyExistsError):
            role_service().create(role_entity)
        repositories.role().create.assert_called_once_with(role_entity)

    def test_get__entity_returned(self, repositories, role_entity, role_service):
        repositories.role().get.return_value = role_entity
        role = role_service().get(role_entity.pk)

        assert role is role_entity
        repositories.role().get.assert_called_once_with(role_entity.pk)

    def test_get__already_exists_error(self, repositories, role_entity, role_service):
        repositories.role().get.side_effect = RoleAlreadyExistsError

        with pytest.raises(RoleAlreadyExistsError):
            role_service().get(role_entity.pk)
        repositories.role().get.assert_called_once_with(role_entity.pk)

    def test_update__entity_returned(self, repositories, role_entity, role_service):
        repositories.role().update.return_value = role_entity
        role = role_service().update(role_entity.pk, role_entity)

        assert role is role_entity
        repositories.role().update.assert_called_once_with(role_entity.pk, role_entity)

    def test_update__already_exists_error(self, repositories, role_entity, role_service):
        repositories.role().update.side_effect = RoleAlreadyExistsError

        with pytest.raises(RoleAlreadyExistsError):
            role_service().update(role_entity.pk, role_entity)
        repositories.role().update.assert_called_once_with(role_entity.pk, role_entity)

    def test_update__not_found_error(self, repositories, role_entity, role_service):
        repositories.role().update.side_effect = RoleNotFoundError

        with pytest.raises(RoleNotFoundError):
            role_service().update(role_entity.pk, role_entity)
        repositories.role().update.assert_called_once_with(role_entity.pk, role_entity)

    def test_delete__none_returned(self, repositories, role_entity, role_service):
        repositories.role().delete.return_value = role_entity
        role = role_service().delete(role_entity.pk)

        assert role is None
        repositories.role().delete.assert_called_once_with(role_entity.pk)

    def test_delete__not_found_error(self, repositories, role_entity, role_service):
        repositories.role().delete.side_effect = RoleNotFoundError

        with pytest.raises(RoleNotFoundError):
            role_service().delete(role_entity.pk)
        repositories.role().delete.assert_called_once_with(role_entity.pk)

    def test_get_list__entity_list_returned(self, repositories, role_entity, role_service):
        role_list = [role_entity, role_entity]
        repositories.role().get_list.return_value = role_list
        res = role_service().get_list()

        assert res is role_list
        repositories.role().get_list.assert_called_once_with()
