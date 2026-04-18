from dataclasses import asdict

import pytest

from deps_iam.domain.dtos import ExpandedUser, UserUpdateObject
from deps_iam.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError


@pytest.fixture
def users_service(services):
    yield services().user()


class TestUserService:
    def test_create_user__user_added(self, users_service, user_entity):
        returned_user = users_service.add(user_entity)
        user_entity.pk = returned_user.pk
        assert user_entity == returned_user

    def test_create_user__already_in_database__raises_exception(self, users_service, user_factory):
        user1, user2 = user_factory.build_batch(2, pk="similar_pk")
        users_service.add(user1)
        with pytest.raises(UserAlreadyExistsError):
            users_service.add(user2)

    def test_get_user__user_not_in_db__raises_not_found(self, users_service):
        with pytest.raises(UserNotFoundError):
            users_service.get("not existing pk")

    def test_get_user__user_exist__valid_user(self, users_service, user_entity):
        entity_in_db = users_service.add(user_entity)
        assert users_service.get(user_entity.pk) == entity_in_db

    def test_get_user__user_exists__return_user(
        self, users_service, organisation_service, user_entity, organisation, config
    ):
        organisation.customization_url = "http://customize"
        org = organisation_service.create_organisation(organisation)
        user_entity.organisation = org.pk
        user_entity = users_service.add(user_entity)

        expanded_user = ExpandedUser(**asdict(user_entity))
        expanded_user.organisation = org
        expanded_user.default_customization_url = config.default_customization_url()

        res = users_service.get_expanded_user(user_entity.pk)

        assert res == expanded_user

    def test_get_users__users_exists__valid_users(self, users_service, user_factory):
        users = user_factory.build_batch(10)
        db_users = [users_service.add(user) for user in users]
        get_users_response = users_service.get_list()
        for user in users:
            assert user in db_users
            assert user in get_users_response

    def test_update_user__user_exists__user_updated(self, users_service, user_factory):
        old_entity, new_entity = user_factory.build_batch(2, pk="similar pk", username="email", email="email")
        new_entity.created_at = old_entity.created_at
        users_service.add(old_entity)
        new_entity_from_db = users_service.update(old_entity.pk, UserUpdateObject.from_entity(new_entity))
        assert users_service.get(old_entity.pk) == new_entity_from_db == new_entity

    def test_update_user__user_not_exists__raises_not_found(self, users_service, user_entity):
        with pytest.raises(UserNotFoundError):
            users_service.update(user_entity.pk, UserUpdateObject.from_entity(user_entity))

    def test_delete_user__user_exists__deleted(self, users_service, user_entity):
        users_service.add(user_entity)
        users_service.delete(user_entity.pk)
        with pytest.raises(UserNotFoundError):
            users_service.get(user_entity.pk)

    def test_delete_user__user_not_exists__raises_exception(self, users_service, user_entity):
        with pytest.raises(UserNotFoundError):
            users_service.delete(user_entity.pk)
