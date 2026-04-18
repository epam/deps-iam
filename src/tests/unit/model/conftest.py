import pytest

from deps_iam.domain.model import User


@pytest.fixture
def test_maga_user(test_user_info, test_tenant, test_personal_info):
    return User(id_=test_user_info.id, tenant_id=test_tenant.id, personal_info=test_personal_info)


@pytest.fixture
def test_second_group_in_tenant(existing_tenant):
    return existing_tenant.create_group("SecondTenantBubbleGroup")
