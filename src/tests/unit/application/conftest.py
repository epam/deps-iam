import pytest


@pytest.fixture
def user_service(maga_services, fake_identity_provider, fake_maga_user_repository):
    return maga_services.user()


@pytest.fixture
def policy_service(maga_services, fake_policy_repository):
    return maga_services.policy()


@pytest.fixture
def group_service(maga_services, fake_tenant_repository, fake_group_repository):
    return maga_services.group()
