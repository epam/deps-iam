from ..group import Group
from ..shared import EntityId, UserInfo
from ..shared.guards import Guard, ImmutableCheck
from ..user import PersonalInfo, User

__all__ = ["Tenant"]


class Tenant:
    id = Guard[EntityId](EntityId, ImmutableCheck())
    name = Guard[str](str)

    def __init__(self, id_: EntityId, name: str):
        self.id = id_
        self.name = name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.id == other.id

    def __str__(self) -> str:
        return f"<Tenant> id: {self.id}, name: {self.name}"

    def create_user(self, user_info: UserInfo) -> User:
        return User(
            id_=user_info.id,
            tenant_id=self.id,
            personal_info=PersonalInfo(
                first_name=user_info.first_name, last_name=user_info.last_name, email=user_info.email
            ),
        )

    def create_group(self, group_name: str) -> Group:
        group_id_entity = EntityId()
        return Group(
            id_=group_id_entity,
            tenant_id=self.id,
            name=group_name,
        )
