from deps_message_flow.events.publisher import DomainEventPublisher

from deps_iam.domain.interfaces.repositories import (
    IOrganisationRepository,
    IPermissionRepository,
    IRoleRepository,
    IUserApiKeyRepository,
    IUserRepository,
)
from deps_iam.extras.interfaces import IUoW


class UnitOfWork(IUoW):
    def __init__(
        self,
        database_uow: IUoW,
        message_uow: IUoW,
        role_repository: IRoleRepository,
        organisation_repository: IOrganisationRepository,
        user_repository: IUserRepository,
        user_api_key_repository: IUserApiKeyRepository,
        permission_repository: IPermissionRepository,
        event_publisher: DomainEventPublisher,
    ):
        self._database_uow = database_uow
        self._message_uow = message_uow

        self.role = role_repository
        self.organisation = organisation_repository
        self.user = user_repository
        self.user_api_key = user_api_key_repository
        self.permission = permission_repository

        self.event_publisher = event_publisher

    def commit(self) -> None:
        self._message_uow.commit()
        self._database_uow.commit()

    def rollback(self) -> None:
        self._message_uow.rollback()
        self._database_uow.rollback()

    def open_transaction(self) -> None:
        self._database_uow.open_transaction()
        self._message_uow.open_transaction()

    def close_transaction(self):
        # order matters
        self._message_uow.close_transaction()
        self._database_uow.close_transaction()
