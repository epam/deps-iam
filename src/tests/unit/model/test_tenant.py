from deps_iam.domain.model import Tenant


def test_create_group__group_created(test_tenant: Tenant):
    new_group = test_tenant.create_group(group_name="deps-admins")

    assert new_group.name.drn.split(":")[2] == test_tenant.id()
    assert f"group/{new_group.id.value}" == new_group.name.drn.split(":")[-1]


def test_tenant_create_user_successful(test_tenant, test_user_info):
    user = test_tenant.create_user(test_user_info)

    assert user.id == test_user_info.id
    assert user.personal_info.first_name == test_user_info.first_name
    assert user.personal_info.last_name == test_user_info.last_name
    assert user.personal_info.email == test_user_info.email
    assert user.tenant_id == test_tenant.id
