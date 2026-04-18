import logging

from deps_message_flow.sagas.orchestration_simple_dsl import SimpleSaga

from ..sagas_data import SignUpSagaData, SignUpSteps

__all__ = ["SignUpSaga"]


class SignUpSaga(SimpleSaga[SignUpSagaData]):
    def __init__(self, steps: SignUpSteps, personal_space_enabled: bool = False) -> None:
        # fmt: off
        self._saga_definition = (
            self.step()
            .invoke_local(steps.authenticate)
            .with_compensation(steps.delete_personal_space)
        )
        # fmt: on
        if personal_space_enabled:
            self._saga_definition = (
                self._saga_definition.step()  # noqa: WPS221
                .invoke_local(steps.create_personal_space)
                .with_compensation(steps.delete_group_policies)
                .step()
                .invoke_local(steps.save_group_policies)
                .with_compensation(steps.delete_user)
                .step()
                .invoke_local(steps.sign_up)
                .with_compensation(steps.delete_user_policies)
                .step()
                .invoke_local(steps.save_user_policies)
            )
        self._saga_definition = self._saga_definition.build()
        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: SignUpSagaData) -> None:
        self._logger.info("SignUpSaga: %s for user: %s is completed successfully", saga_id, data.user.id())

    def on_saga_failed(self, saga_id: str, data: SignUpSagaData) -> None:
        self._logger.error("SignUpSaga: %s for user: %s is failed", saga_id, data.to_dict())

    def on_saga_rolled_back(self, saga_id: str, data: SignUpSagaData) -> None:
        self._logger.error("SignUpSaga: %s with data: %s is rolled back", saga_id, data.to_dict())
