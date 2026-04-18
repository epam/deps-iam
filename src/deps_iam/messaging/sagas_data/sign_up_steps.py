import logging

from deps_iam.application import GroupService, PolicyService, UserService
from deps_iam.infrastructure.services import OpenIdIdentityProvider
from deps_iam.messaging.sagas_data.sign_up_data import SignUpSagaData

__all__ = ["SignUpSteps"]


class SignUpSteps:
    def __init__(
        self,
        group_service: GroupService,
        user_service: UserService,
        policy_service: PolicyService,
        identity_provider: OpenIdIdentityProvider,
    ) -> None:
        self._group_service = group_service
        self._user_service = user_service
        self._policy_service = policy_service
        self._identity_provider = identity_provider

        self._logger = logging.getLogger(self.__class__.__name__)

    def authenticate(self, data: SignUpSagaData) -> None:
        data.user_info = self._identity_provider.authenticate(data.access_token)
        self._logger.debug(
            "Step authenticate has been finished. User_id: %s, email: %s"
            % (data.user_info.id(), data.user_info.email())
        )

    def create_personal_space(self, data: SignUpSagaData) -> None:
        data.group = self._group_service.create_personal_space(data.tenant_id, data.user_info)
        self._logger.debug("Step create_personal_space has been finished. Group_id %s" % data.group.id())

    def delete_personal_space(self, data: SignUpSagaData) -> None:
        if data.group:
            self._group_service.delete_personal_space(data.group.id)

    def save_group_policies(self, data: SignUpSagaData) -> None:
        self._policy_service.save_group_policies(data.group)
        self._logger.debug(
            "Step save_group_policies has been finished. Group policies: %s"
            % [data.group.name.drn, *[data.group.roles[role].name.drn for role in data.group.roles]]
        )

    def delete_group_policies(self, data: SignUpSagaData) -> None:
        self._policy_service.delete_policies(
            [data.group.name.drn, *[data.group.roles[role].name.drn for role in data.group.roles]]  # noqa: WPS219
        )

    def sign_up(self, data: SignUpSagaData) -> None:
        user = self._user_service.sign_up(data.user_info, data.group)
        data.user = user
        self._logger.debug(
            "Step sign_up has been finished. User_id: %s, active_group: %s"
            % (data.user.id(), data.user.active_group.group.name)
        )

    def delete_user(self, data: SignUpSagaData) -> None:
        if data.user:
            self._user_service.delete(data.user)

    def save_user_policies(self, data: SignUpSagaData) -> None:
        self._policy_service.save_user_policies(data.user)
        self._logger.debug("Step save_user_policies has been finished. User policies: %s" % data.user.drn)

    def delete_user_policies(self, data: SignUpSagaData) -> None:
        self._policy_service.delete_policies(data.user.drn)
