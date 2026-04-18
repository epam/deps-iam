from uuid import uuid4

import pytest

from deps_iam.domain.dtos import UserUpdateObject
from deps_iam.domain.exceptions import (
    UserAlreadyExistsError,
    UserApiKeyNotFoundError,
    UserNotFoundError,
)

API_KEY = uuid4()
USER_PK = uuid4()


@pytest.fixture
def user_service(services, repositories):
    services.user.reset_override()
    yield services.user()


def test_create_user__user_added(user_entity, user_service, user_repository_mock):
    user_repository_mock.add.return_value = user_entity
    returned_user = user_service.add(user_entity)
    returned_user.pk = user_entity.pk
    assert user_entity == returned_user


def test_create_user__already_in_database__raises_exception(user_entity, user_service, user_repository_mock):
    user_repository_mock.add.side_effect = UserAlreadyExistsError
    with pytest.raises(UserAlreadyExistsError):
        user_service.add(user_entity)


def test_get_user__user_exist__valid_user(user_entity, user_service, user_repository_mock):
    user_repository_mock.get.return_value = user_entity
    result = user_service.get(user_entity.pk)
    assert result == user_entity


def test_get_user__user_not_in_db__raises_not_found(user_service, user_repository_mock):
    user_repository_mock.get.side_effect = UserNotFoundError
    with pytest.raises(UserNotFoundError):
        user_service.get("not existing pk")


def test_get_expanded_user__user_exist__valid_user(expanded_user, user_service, user_repository_mock):
    user_repository_mock.get_expanded_user.return_value = expanded_user
    result = user_service.get_expanded_user(expanded_user.pk)
    assert result == expanded_user


def test_get_expanded_user__user_not_in_db__raises_not_found(user_service, user_repository_mock):
    user_repository_mock.get_expanded_user.side_effect = UserNotFoundError
    with pytest.raises(UserNotFoundError):
        user_service.get_expanded_user("not existing pk")


def test_get_expanded_user__customization_service_called(user_service, customization_service_mock):
    user_service.get_expanded_user("pk")

    customization_service_mock.enrich_customization_settings_for_user.assert_called()


def test_get_users__users_exists__valid_users(user_factory, user_service, user_repository_mock):
    users = user_factory.build_batch(10)
    user_repository_mock.get_list.return_value = [user_entity for user_entity in users]
    get_users_response = user_service.get_list()
    for user in users:
        assert user in users
        assert user in get_users_response


def test_get_users__not_all_users_exists__raises_exception(user_service, user_repository_mock):
    user_repository_mock.get_list.side_effect = UserNotFoundError
    with pytest.raises(UserNotFoundError):
        user_service.get_list()


def test_update_user__user_exists__user_updated(user_factory, user_service, user_repository_mock):
    old_entity, new_entity = user_factory.build_batch(2, pk="similar pk", username="email", email="email")
    user_repository_mock.update.return_value = new_entity
    new_entity_from_db = user_service.update(old_entity.pk, UserUpdateObject.from_entity(new_entity))
    assert new_entity_from_db == new_entity


def test_update_user__user_not_exists__raises_not_found(user_entity, user_service, user_repository_mock):
    user_repository_mock.update.side_effect = UserNotFoundError
    with pytest.raises(UserNotFoundError):
        user_service.update(user_entity.pk, user_entity)


def test_delete_user__user_exists__deleted(user_entity, user_service, user_repository_mock):
    user_repository_mock.delete.return_value = True
    user_service.delete(user_entity.pk)
    assert True


def test_delete_user__user_not_exists__raises_exception(user_entity, user_service, user_repository_mock):
    user_repository_mock.delete.side_effect = UserNotFoundError
    with pytest.raises(UserNotFoundError):
        user_service.delete(user_entity.pk)


def test_create_uak__user_exists__uak_returned(user_service, user_api_key_repository_mock):
    user_api_key_repository_mock.create.return_value = API_KEY
    api_key = user_service.create_api_key(USER_PK)
    assert api_key == API_KEY


def test_create_uak__user_no_exists__user_not_found(user_service, user_api_key_repository_mock):
    user_api_key_repository_mock.create.side_effect = UserNotFoundError
    with pytest.raises(UserNotFoundError):
        user_service.create_api_key(USER_PK)


def test_get_uak__uak_exists__returned(user_service, user_api_key_repository_mock):
    user_api_key_repository_mock.get.return_value = API_KEY
    api_key = user_service.get_api_key(USER_PK)
    assert api_key == API_KEY


def test_get_uak__uak_no_exists__uak_not_found(user_service, user_api_key_repository_mock):
    user_api_key_repository_mock.get.side_effect = UserApiKeyNotFoundError
    with pytest.raises(UserApiKeyNotFoundError):
        user_service.get_api_key(USER_PK)


def test_delete_uak__uak_exists__none(user_service, user_api_key_repository_mock):
    user_api_key_repository_mock.delete.return_value = None
    res = user_service.delete_api_key(USER_PK)
    assert res is None


def test_delete_uak__uak_no_exists__returned(user_service, user_api_key_repository_mock):
    user_api_key_repository_mock.delete.side_effect = UserApiKeyNotFoundError
    with pytest.raises(UserApiKeyNotFoundError):
        user_service.delete_api_key(USER_PK)


def test_get_user_by_api_key__user_exists__returned(
    user_entity, user_service, user_repository_mock, user_api_key_repository_mock
):
    def get_user_entity(*args):
        if args[0] == user_entity.pk:
            return user_entity

    user_api_key_repository_mock.get_user_by_api_key.return_value = user_entity.pk
    user_repository_mock.get.side_effect = get_user_entity
    user = user_service.get_user_by_api_key(str(API_KEY))
    assert user == user_entity


def test_get_user_by_api_key__user_no_exists__user_not_found(user_service, user_api_key_repository_mock):
    user_api_key_repository_mock.get_user_by_api_key.side_effect = UserNotFoundError
    with pytest.raises(UserNotFoundError):
        user_service.get_user_by_api_key(str(API_KEY))
