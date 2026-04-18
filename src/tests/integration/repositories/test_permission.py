import pytest

from deps_iam.domain.entities import PermissionEntity
from deps_iam.domain.exceptions import (
    PermissionAlreadyExistsError,
    PermissionNotFoundError,
)


class TestPermissionRepository:
    def test_request__add_permission__get_valid_permission(self, repositories, permission_entity):
        permission = repositories.permission().add(permission_entity)
        assert repositories.permission().get_list() == [permission]

    def test_add_permission__already_exists_error(self, repositories, permission_entity):
        permission = repositories.permission().add(permission_entity)
        with pytest.raises(PermissionAlreadyExistsError):
            repositories.permission().add(permission)

    def test_request__del_permission(self, repositories, permission_entity):
        permission = repositories.permission().add(permission_entity)
        repositories.permission().delete(permission)
        assert repositories.permission().get_list() == []

    def test_request__del_permission__not_found_error(self, repositories):
        with pytest.raises(PermissionNotFoundError):
            repositories.permission().delete(PermissionEntity("test"))
