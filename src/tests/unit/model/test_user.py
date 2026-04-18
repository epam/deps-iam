def test_user_join_group__successful(test_maga_user, test_personal_group):
    test_maga_user.join_group(test_personal_group)

    assert test_maga_user.active_group.group == test_personal_group.name
    assert test_maga_user.active_group.role == test_personal_group.role_of_user(test_maga_user.id()).name


def test_user_join_group__group_has_been_set__active_group_hasnot_changed(
    test_maga_user, test_personal_group, test_second_group_in_tenant
):
    test_maga_user.join_group(test_personal_group)
    test_second_group_in_tenant.accept(test_maga_user.id)
    test_maga_user.join_group(test_second_group_in_tenant)

    assert test_maga_user.active_group.group == test_personal_group.name
    assert test_maga_user.active_group.role == test_personal_group.role_of_user(test_maga_user.id()).name


def test_user_join_group__group_added_to_groups(test_maga_user, test_personal_group, test_second_group_in_tenant):
    test_maga_user.join_group(test_personal_group)
    test_second_group_in_tenant.accept(test_maga_user.id)
    test_maga_user.join_group(test_second_group_in_tenant)

    assert len(test_maga_user.groups) == 2
    assert test_second_group_in_tenant.id() in test_maga_user.groups
    assert test_maga_user.groups[test_second_group_in_tenant.id()] == test_second_group_in_tenant


def test_user_join_group__group_already_added__group_not_added_to_group(test_maga_user, test_personal_group):
    test_maga_user.join_group(test_personal_group)
    test_maga_user.join_group(test_personal_group)

    assert len(test_maga_user.groups) == 1
