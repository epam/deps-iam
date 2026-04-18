from unittest.mock import patch

from deps_message_flow.sagas.testing_support import *

from deps_iam.messaging.sagas import SignUpSaga


def test_sign_up__successful(sign_up_steps, sign_up_saga_data, fake_maga_user_repository, fake_tenant_repository):
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            SignUpSaga(sign_up_steps, personal_space_enabled=True),
            sign_up_saga_data,
        )
        .expect_completed_successfully()
    )

    entity_id = suts.saga_data["entity_id"]
    assert entity_id == fake_maga_user_repository.db[entity_id].id()
    assert fake_maga_user_repository.db[entity_id].tenant_id()
    assert len(fake_maga_user_repository.db[entity_id].groups) == 1


def test_sign_up__personal_space_disabled__user_hasnt_created(
    sign_up_steps, sign_up_saga_data, fake_maga_user_repository
):
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            SignUpSaga(sign_up_steps, personal_space_enabled=False),
            sign_up_saga_data,
        )
        .expect_completed_successfully()
    )
    assert len(fake_maga_user_repository.db.items()) == 0


def test_sign_up__error_occured__rolled_back(
    sign_up_steps, sign_up_saga_data, fake_maga_user_repository, fake_group_repository, fake_policy_repository
):
    with patch("deps_iam.application.policy.PolicyService.save_user_policies") as mock:
        mock.side_effect = RuntimeError
        (
            SagaUnitTestSupport.given()
            .saga(
                SignUpSaga(sign_up_steps, personal_space_enabled=True),
                sign_up_saga_data,
            )
            .expect_rolled_back()
        )

        assert fake_maga_user_repository.db == {}
        assert fake_group_repository._db == {}
        assert fake_policy_repository._policy_db == {}
