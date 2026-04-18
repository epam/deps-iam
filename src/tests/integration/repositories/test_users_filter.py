import pytest

from deps_iam.domain.dtos import UserListFilter


class TestUsersFilters:
    def test_get_users__no_filter__all_users(self, user_repository, user_factory):
        users = user_factory.build_batch(10)
        db_users = [user_repository.add(user) for user in users]
        get_users_response = user_repository.get_list()
        for user in users:
            assert user in db_users
            assert user in get_users_response

    def test_get_users__filter_pks__valid_users(self, user_repository, user_factory):
        users = [user_repository.add(user) for user in user_factory.build_batch(10)]
        expected_users, unexpected_users = users[:6], users[6:]
        expected_users_pks = [user.pk for user in expected_users]
        get_users_response = user_repository.get_list(UserListFilter(pks=expected_users_pks))
        assert get_users_response
        for user in get_users_response:
            assert user in expected_users
            assert user not in unexpected_users

    def test_get_users__filter_pks_one_pk__valid_users(self, user_repository, user_factory):
        users = [user_repository.add(user) for user in user_factory.build_batch(10)]
        expected_user, *unexpected_users = users
        get_users_response = user_repository.get_list(UserListFilter(pks=[expected_user.pk]))
        assert get_users_response == [expected_user]

    @pytest.mark.parametrize("attribute", ["username", "email", "first_name", "last_name"])
    def test_get_users__filter_username__valid_users(self, user_repository, user_factory, attribute):
        users = user_factory.build_batch(10)
        for index, user in enumerate(users[:5]):
            user.__dict__[attribute] = users[0].__dict__[attribute] + str(index)
        user_filter = UserListFilter(username=users[0].__dict__[attribute])
        get_users_response = user_repository.get_list(user_filter)
        for user in get_users_response:
            assert user in users[:5]
            assert user not in users[5:]

    def test_get_users__filter_email__valid_users(self, user_repository, user_factory):
        user_repository.add(user_factory(email="test@test.com"))
        user_repository.add(user_factory(email="ttest@test.com"))

        get_users_response = user_repository.get_list(UserListFilter(email="test@test.com"))

        assert len(get_users_response) == 1
        assert get_users_response[0].email == "test@test.com"
