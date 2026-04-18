import logging

from deps_message_flow.sagas.orchestration import Saga, SagaInstanceFactory

from deps_iam.domain.model import EntityId
from deps_iam.messaging.sagas import SignUpSaga
from deps_iam.messaging.sagas_data.sign_up_data import SignUpSagaData


class SignUpService:
    def __init__(
        self,
        sagas: list[Saga],
        saga_instance_factory: SagaInstanceFactory,
    ) -> None:
        self._sagas = {saga.__class__: saga for saga in sagas}
        self._saga_instance_factory = saga_instance_factory

        self._logger = logging.getLogger(self.__class__.__name__)

    def sign_up(
        self,
        access_token: str,
        tenant_id: EntityId,
    ) -> None:
        sd = SignUpSagaData(access_token=access_token, tenant_id=tenant_id)
        self._saga_instance_factory.create(self._sagas[SignUpSaga], sd)
