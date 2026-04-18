import logging

from deps_iam.domain.model import (
    EntityId,
    Group,
    IGroupRepository,
    ITenantRepository,
    UserInfo,
)

__all__ = ["GroupService"]


class GroupService:
    def __init__(self, tenant_repository: ITenantRepository, group_repository: IGroupRepository):
        self._tenant_repository = tenant_repository
        self._group_repository = group_repository

        self._logger = logging.getLogger(self.__class__.__name__)

    def create_personal_space(self, tenant_id: EntityId, user_info: UserInfo) -> Group:
        tenant = self._tenant_repository.tenant_of_id(tenant_id())
        group = tenant.create_group(group_name=f"{user_info.first_name} {user_info.last_name} Group")

        group.accept(user_info.id)
        group.give_ownership(user_info.id)
        self._group_repository.save(group)

        return group

    def delete_personal_space(self, group_id: EntityId) -> None:
        self._group_repository.delete(group_id())

    def join(self, group_id: EntityId, user_info: UserInfo) -> Group:
        group = self._group_repository.group_of_id(group_id())
        group.join(user_info)
        self._group_repository.save(group)
        return group
