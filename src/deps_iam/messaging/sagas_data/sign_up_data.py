from typing import Optional

from deps_message_flow.sagas.orchestration import SagaData

from deps_iam.domain.model import EntityId, Group, User, UserInfo

__all__ = ["SignUpSagaData"]


class SignUpSagaData(SagaData):
    def __init__(
        self,
        access_token: str,
        tenant_id: EntityId,
        *,
        user_info: Optional[UserInfo] = None,
        group: Optional[Group] = None,
        user: Optional[User] = None,
    ):
        super().__init__(entity_id=user_info.id() if user_info else None)
        self.access_token = access_token
        self.tenant_id = tenant_id
        self.user_info = user_info
        self.group = group
        self.user = user

    @property
    def user_info(self) -> Optional[UserInfo]:
        return self._user_info

    @user_info.setter
    def user_info(self, value: Optional[UserInfo]) -> None:
        self.entity_id = value.id() if value else None
        self._user_info = value
