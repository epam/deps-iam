import logging

from deps_iam.domain.model import (
    Group,
    IIdentityProvider,
    ITenantRepository,
    IUserRepository,
    User,
    UserInfo,
)

__all__ = ["UserService"]


class UserService:
    def __init__(
        self,
        identity_provider: IIdentityProvider,
        user_repository: IUserRepository,
        tenant_repository: ITenantRepository,
    ) -> None:
        self._identity_provider = identity_provider
        self._user_repository = user_repository
        self._tenant_repository = tenant_repository
        self._logger = logging.getLogger(self.__class__.__name__)

    def sign_in(self, access_token: str) -> bool:
        user_info = self._identity_provider.authenticate(access_token=access_token)
        return self._user_repository.has_user_with_id(id_=user_info.id)

    def sign_up(self, userinfo: UserInfo, group: Group) -> User:
        tenant = self._tenant_repository.tenant_of_id(group.tenant_id())
        user = tenant.create_user(userinfo)
        user.join_group(group)
        self._user_repository.save(user)
        return user

    def delete(self, user: User) -> None:
        self._user_repository.delete(user.id())
