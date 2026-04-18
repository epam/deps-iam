import pytest

from deps_iam.messaging.sagas_data import SignUpSagaData, SignUpSteps


@pytest.fixture
def sign_up_steps(
    fake_identity_provider,
    maga_group_service,
    maga_policy_service,
    maga_user_service,
    fake_tenant_repository,
):
    return SignUpSteps(
        maga_group_service,
        maga_user_service,
        maga_policy_service,
        fake_identity_provider,
    )


@pytest.fixture
def sign_up_saga_data(test_token, existing_tenant, fake_tenant_repository):
    return SignUpSagaData(access_token=test_token, tenant_id=existing_tenant.id)
