from uuid import UUID, uuid4

import pytest

from deps_iam.domain.exceptions import UserApiKeyNotFoundError, UserNotFoundError


class TestUserApiKeyRepository:
    api_key = uuid4()

    def test_create__ak_no_exists__user_exists__created(self, existing_user, user_api_key_repository):
        api_key = user_api_key_repository.create(existing_user.pk, self.api_key)
        assert isinstance(api_key, str)
        assert api_key != existing_user.pk
        assert api_key == str(UUID(api_key, version=4))

    def test_create__ak_exists__new_created(self, existing_user, user_api_key_repository):
        api_key = user_api_key_repository.create(existing_user.pk, self.api_key)
        new_api_key = user_api_key_repository.create(existing_user.pk, uuid4())
        assert api_key != new_api_key

    def test_create__ak_no_exists__user_no_exists__error(self, user_api_key_repository):
        with pytest.raises(UserNotFoundError):
            user_api_key_repository.create("user_pk", self.api_key)

    def test_get__ak_no_exists__user_exists__error(self, existing_user, user_api_key_repository):
        with pytest.raises(UserApiKeyNotFoundError):
            user_api_key_repository.get(existing_user.pk)

    def test_get__ak_no_exists__user_no_exists__error(self, user_api_key_repository):
        with pytest.raises(UserApiKeyNotFoundError):
            user_api_key_repository.get("user_pk")

    def test_get__ak_exists__user_exists__gotten(self, existing_user, user_api_key_repository):
        api_key = user_api_key_repository.create(existing_user.pk, self.api_key)
        res = user_api_key_repository.get(existing_user.pk)
        assert res == api_key

    def test_delete__ak_no_exists__user_no_exists__error(self, user_api_key_repository):
        with pytest.raises(UserApiKeyNotFoundError):
            user_api_key_repository.delete("user_pk")

    def test_delete__ak_no_exists__user_exists__error(self, existing_user, user_api_key_repository):
        with pytest.raises(UserApiKeyNotFoundError):
            user_api_key_repository.delete(existing_user.pk)

    def test_delete__ak_exists__user_exists__deleted(self, existing_user, user_api_key_repository):
        user_api_key_repository.create(existing_user.pk, self.api_key)
        user_api_key_repository.get(existing_user.pk)
        user_api_key_repository.delete(existing_user.pk)
        with pytest.raises(UserApiKeyNotFoundError):
            user_api_key_repository.get(existing_user.pk)

    def test_get_user_by_api_key__ak_no_exists__user_no_exists__error(self, user_api_key_repository):
        with pytest.raises(UserNotFoundError):
            user_api_key_repository.get_user_by_api_key("not existing api key")

    def test_get_user_by_api_key__ak_exists__user_exists__gotten(self, existing_user, user_api_key_repository):
        user_api_key_repository.create(existing_user.pk, self.api_key)
        res = user_api_key_repository.get_user_by_api_key(str(self.api_key))
        assert res == existing_user.pk
