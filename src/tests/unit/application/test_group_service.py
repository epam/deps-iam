from unittest import mock


def test__create_personal_space__success(
    group_service, fake_group_repository, fake_tenant_repository, test_tenant, test_user_info
):
    fake_tenant_repository._db[test_tenant.id()] = test_tenant

    group = group_service.create_personal_space(test_tenant.id, test_user_info)

    assert group.name.name == f"{test_user_info.first_name} {test_user_info.last_name} Group"
    assert group.name.drn == f"drn:iam:{test_tenant.id.value}:group/{group.id.value}"
    assert len(group.roles) == 2
    assert group.roles["owner"].group_id == group.id
    assert group.roles["owner"].name.name == "owner"
    assert group.roles["owner"].name.drn == f"drn:iam:{test_tenant.id.value}:group/{group.id.value}/role/owner"
    assert group.roles["user"].name.name == "user"
    assert group.roles["user"].name.drn == f"drn:iam:{test_tenant.id.value}:group/{group.id.value}/role/user"
    assert group.users == [test_user_info.id]
    assert group.role_of_user(test_user_info.id.value) == group.roles["owner"]
    assert fake_group_repository._db[group.id.value] == group


def test__delete_personal_space(group_service, test_personal_group, fake_group_repository):
    fake_group_repository.save(test_personal_group)
    group_service.delete_personal_space(test_personal_group.id)

    assert not fake_group_repository._db


@mock.patch("deps_iam.domain.model.group.group.Group._is_user_invited")
def test__join__user_invited__success(
    invited_mock, group_service, fake_group_repository, existing_group, user_info_factory
):
    user_info = user_info_factory()
    invited_mock.return_value = True
    group_service.join(existing_group.id, user_info)

    saved_group = fake_group_repository._db[existing_group.id()]

    assert user_info.id in saved_group.users


@mock.patch("deps_iam.domain.model.group.group.Group._is_user_invited")
def test__join__user_in_group__no_errors(
    invited_mock, group_service, fake_group_repository, existing_group, user_info_factory
):
    invited_mock.return_value = True
    user_info = user_info_factory()
    group_service.join(existing_group.id, user_info)
    group_service.join(existing_group.id, user_info)
    group_service.join(existing_group.id, user_info)
    saved_group = fake_group_repository._db[existing_group.id()]

    assert user_info.id in saved_group.users
    assert len(saved_group.users) == 2


@mock.patch("deps_iam.domain.model.group.group.Group._is_user_invited")
def test__join__user_not_invited__approval_request_created(
    invited_mock, group_service, fake_group_repository, existing_group, user_info_factory
):
    user_info = user_info_factory()
    invited_mock.return_value = False
    group_service.join(existing_group.id, user_info)

    saved_group = fake_group_repository._db[existing_group.id()]

    assert user_info.id not in saved_group.users
    assert user_info in saved_group.approval_requests


@mock.patch("deps_iam.domain.model.group.group.Group._is_user_invited")
def test__join__user_not_invited__joined_twice__one_approval_request(
    invited_mock, group_service, fake_group_repository, existing_group, user_info_factory
):
    user_info = user_info_factory()
    invited_mock.return_value = False
    group_service.join(existing_group.id, user_info)
    group_service.join(existing_group.id, user_info)

    saved_group = fake_group_repository._db[existing_group.id()]

    assert user_info.id not in saved_group.users
    assert user_info in saved_group.approval_requests
    assert len(saved_group.approval_requests) == 1
