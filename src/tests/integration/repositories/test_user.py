import pytest

from deps_iam.domain.dtos import UserUpdateObject
from deps_iam.domain.entities import UserEntity
from deps_iam.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError
from tests.factories import OrganisationFactory


@pytest.fixture(params=(None, OrganisationFactory()))
def expanded_user(expanded_user, organisation_repository, request):
    expanded_user.organisation = request.param
    if expanded_user.organisation:
        organisation_repository.create(expanded_user.organisation)
    return expanded_user


class TestUserRepository:
    def test_create_user__user_added(self, user_repository, user_entity):
        returned_user = user_repository.add(user_entity)
        user_entity.pk = returned_user.pk
        assert user_entity == returned_user

    def test_create_user__already_in_database__raises_exception(self, user_repository, user_factory):
        user1, user2 = user_factory.build_batch(2, pk="similar_pk")
        user_repository.add(user1)
        with pytest.raises(UserAlreadyExistsError):
            user_repository.add(user2)

    def test_get_user__user_not_in_db__raises_not_found(self, user_repository):
        with pytest.raises(UserNotFoundError):
            user_repository.get("not existing pk")

    def test_get_user__user_exist__valid_user(self, user_repository, user_entity):
        entity_in_db = user_repository.add(user_entity)
        assert user_repository.get(user_entity.pk) == entity_in_db

    def test_get_expanded_user__user_exists__return_user(self, user_repository, expanded_user):
        org_pk = expanded_user.organisation.pk if expanded_user.organisation else None
        entity_in_db = user_repository.add(
            UserEntity(
                pk=expanded_user.pk,
                created_at=expanded_user.created_at,
                first_name=expanded_user.first_name,
                last_name=expanded_user.last_name,
                username=expanded_user.username,
                email=expanded_user.email,
                organisation=org_pk,
            )
        )
        assert user_repository.get_expanded_user(entity_in_db.pk) == expanded_user

    def test_get_expanded_user__user_not_in_db__raises_not_found(self, user_repository):
        with pytest.raises(UserNotFoundError):
            user_repository.get_expanded_user("not existing pk")

    def test_get_users__users_exists__valid_users(self, user_repository, user_factory):
        users = user_factory.build_batch(10)
        db_users = [user_repository.add(user) for user in users]
        get_users_response = user_repository.get_list()
        for user in users:
            assert user in db_users
            assert user in get_users_response

    def test_update_user__user_exists__user_updated(self, user_repository, user_factory):
        old_entity, new_entity = user_factory.build_batch(2, pk="similar pk", username="email", email="email")
        new_entity.created_at = old_entity.created_at
        user_repository.add(old_entity)
        update_object = UserUpdateObject.from_entity(new_entity)
        new_entity_from_db = user_repository.update(old_entity.pk, update_object)
        assert user_repository.get(old_entity.pk) == new_entity_from_db == new_entity

    def test_update_user__user_not_exists__raises_not_found(self, user_repository, user_entity):
        with pytest.raises(UserNotFoundError):
            user_repository.update(user_entity.pk, UserUpdateObject.from_entity(user_entity))

    def test_delete_user__user_exists__deleted(self, user_repository, user_entity):
        user_repository.add(user_entity)
        user_repository.delete(user_entity.pk)
        with pytest.raises(UserNotFoundError):
            user_repository.get(user_entity.pk)

    def test_delete_user__user_not_exists__raises_exception(self, user_repository, user_entity):
        with pytest.raises(UserNotFoundError):
            user_repository.delete(user_entity.pk)

    def test_upsert_user__new_user__user_added(self, user_repository, user_entity):
        user_repository.upsert(user_entity)
        user_in_db = user_repository.get(user_entity.pk)

        assert user_entity == user_in_db

    def test_upsert_user__user_exists__user_updated(self, user_repository, user_entity):
        user = user_repository.upsert(user_entity)
        user_entity_not_changed = user_entity
        user_not_changed = user_repository.upsert(user_entity_not_changed)

        assert len(user_repository.get_list()) == 1
        assert user == user_not_changed

    def test_upsert_user__user_exists_info_changed__user_updated(self, user_repository, user_entity):
        user_repository.upsert(user_entity)
        user_entity_changed = user_entity
        user_entity_changed.first_name = "changed_first_name"
        user_repository.upsert(user_entity_changed)
        user_in_db = user_repository.get(user_entity.pk)

        assert len(user_repository.get_list()) == 1
        assert user_in_db.first_name == "changed_first_name"

    def test_deactivate_user_organisation__user_exists__org_deactivated(self, user_repository, user_entity):
        user_repository.add(user_entity)
        user_repository.deactivate_user_organisation(user_entity.pk)

        assert user_entity.organisation is None
