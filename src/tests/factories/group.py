import factory

from deps_iam.domain.model import EntityId, Group

from .maga_user import EntityNameFactory
from .role import RoleFactory

__all__ = ["GroupFactory"]


class GroupFactory(factory.Factory):
    class Meta:
        model = Group

    id_ = factory.LazyFunction(EntityId)
    tenant_id = factory.LazyFunction(EntityId)
    name = factory.SubFactory(EntityNameFactory)
    users = factory.List([factory.LazyFunction(EntityId) for _ in range(3)])
    roles = factory.List([factory.SubFactory(RoleFactory) for _ in range(3)])
