import pytest
from pytest import raises

from deps_iam.domain.exceptions import (
    PermissionAlreadyExistsError,
    PermissionNotFoundError,
)
from tests.factories.permission_entity import PermissionEntityFactory


@pytest.fixture
def permission_service(services):
    services.permission.reset_override()
    yield services.permission()


class TestPermissionService:
    def test_add__new_permission__successfully(self, permission_repository_mock, permission_service):
        permission = PermissionEntityFactory()
        permission_repository_mock.add.return_value = permission

        response = permission_service.add(PermissionEntityFactory)

        assert response == permission

    def test_add__existing_permission__raise_error(self, permission_repository_mock, permission_service):
        permission_repository_mock.add.side_effect = PermissionAlreadyExistsError

        with raises(PermissionAlreadyExistsError):
            permission_service.add(PermissionEntityFactory)

    def test_delete__existing_permission__success(self, permission_repository_mock, permission_service):
        permission_repository_mock.delete.return_value = True
        response = permission_service.delete("Test permission")

        assert response is True

    def test_delete__not_existing_permission__raise_error(self, permission_repository_mock, permission_service):
        permission_repository_mock.delete.side_effect = PermissionNotFoundError

        with pytest.raises(PermissionNotFoundError):
            permission_service.delete("Test permission")

    def test_get__exists_list_permissions__success(self, permission_service, permission_repository_mock):
        permissions_list = [PermissionEntityFactory().name for entity in range(3)]
        permission_repository_mock.get_list.return_value = permissions_list

        response = permission_service.get_list()

        assert response == permissions_list

    def test_get__empty_list_permissions__return_empty_list(self, permission_service, permission_repository_mock):
        permission_repository_mock.get_list.return_value = []

        response = permission_service.get_list()

        assert response == []
