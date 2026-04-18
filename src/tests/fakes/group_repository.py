from typing import Any

from deps_iam.domain.model.group import Group, IGroupRepository
from deps_iam.domain.model.group.group import Group


class FakeGroupRepository(IGroupRepository):
    def __init__(self):
        self._db: dict[str, Any] = {}

    def save(self, group: Group) -> None:
        self._db[group.id.value] = group

    def delete(self, group_id: str) -> None:
        self._db.pop(group_id, None)

    def group_of_id(self, group_id: str) -> Group:
        return self._db[group_id]
