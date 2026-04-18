from typing import Any

from deps_iam.domain.model import EntityId, IUserRepository, User

__all__ = ["FakeUserRepository"]


class FakeUserRepository(IUserRepository):
    def __init__(self) -> None:
        self.db: dict[str, User] = {}

    def user_of_id(self, id_: EntityId) -> User:
        return self.db[id_()]

    def has_user_with_id(self, id_: EntityId) -> bool:
        return bool(self.db.get(id_()))

    def save(self, user: User) -> None:
        self.db[user.id()] = user

    def delete(self, user_id: str) -> None:
        self.db.pop(user_id, None)
