import pytest

from deps_iam.domain.exceptions import UserNotFoundError
from deps_iam.domain.model import EntityId, Group, RoleType, Tenant, UserInfo


def test_create_new_group__roles_initiated(test_tenant: Tenant):
    new_group = test_tenant.create_group(group_name="deps-admins")

    assert new_group.roles.get(RoleType.OWNER.value) is not None
    assert new_group.roles.get(RoleType.USER.value) is not None


def test_create_new_group__group_name_created(test_tenant: Tenant):
    new_group = test_tenant.create_group(group_name="deps-admins")

    assert new_group.name.name == "deps-admins"
    assert new_group.name.drn == f"drn:iam:{new_group.tenant_id.value}:group/{new_group.id.value}"


def test_accept_user__user_accepted__default_role_added(test_group: Group, user_id_entity: EntityId):
    test_group.accept(user_id_entity)

    user_role = test_group.roles[RoleType.USER.value]

    assert test_group.users == [user_id_entity]
    assert test_group.role_of_user(user_id_entity()) == user_role


def test_give_ownership__user_role_updated(test_group: Group, user_id_entity: EntityId):
    test_group.accept(user_id_entity)
    test_group.give_ownership(user_id_entity)

    owner_role = test_group.roles[RoleType.OWNER.value]

    assert test_group.role_of_user(user_id_entity()) == owner_role


def test_give_ownership__user_does_not_exist__raise_error(test_group: Group, user_id_entity: EntityId):
    with pytest.raises(UserNotFoundError):
        test_group.give_ownership(user_id_entity)


def test_join__user_added(test_group: Group, test_user_info: UserInfo, mocker):
    test_group._is_user_invited = mocker.Mock(return_value=True)
    test_group.join(test_user_info)

    assert len(test_group.users) == 1
    assert test_user_info.id in test_group.users


def test_join__user_in_group__user_not_added(test_group, test_user_info, mocker):
    test_group._is_user_invited = mocker.Mock(return_value=True)
    test_group.join(test_user_info)
    test_group.join(test_user_info)

    assert len(test_group.users) == 1


def test_join__user_not_invited__approve_request_added(test_group, test_user_info, mocker):
    test_group._is_user_invited = mocker.Mock(return_value=False)
    test_group.join(test_user_info)

    assert len(test_group.approval_requests) == 1
