from deps_iam.application.user import UserService


def test_sign_up__successful(
    user_service: UserService,
    test_user_info,
    test_personal_group,
    fake_user_repository,
):
    user = user_service.sign_up(test_user_info, test_personal_group)

    assert user.active_group.group == test_personal_group.name
    assert user.active_group.role == test_personal_group.role_of_user(user.id()).name
    assert fake_user_repository.db[user.id()]


def test_sign_up__user_already_exists__no_errors(user_service: UserService, test_user_info, test_personal_group):
    first = user_service.sign_up(test_user_info, test_personal_group)
    second = user_service.sign_up(test_user_info, test_personal_group)

    assert first == second


def test_sign_up__user_already_exists__new_personal_info__no_errors(
    user_service: UserService, test_user_info, test_personal_group, fake_user_repository, user_info_factory
):
    user = user_service.sign_up(test_user_info, test_personal_group)
    new_personal_info = user_info_factory(user_info_id_=user.id())
    user_service.sign_up(new_personal_info, test_personal_group)

    saved_user = fake_user_repository.db[user.id()]

    assert saved_user.personal_info.last_name == new_personal_info.last_name
    assert saved_user.personal_info.first_name == new_personal_info.first_name
    assert saved_user.personal_info.email == new_personal_info.email
    assert saved_user.id == user.id


def test_delete_user__successful(user_service, existing_maga_user, fake_user_repository):
    assert fake_user_repository.db
    user_service.delete(existing_maga_user)
    assert not fake_user_repository.db
