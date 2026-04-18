from factory import Factory, LazyAttribute, LazyFunction, SubFactory, fuzzy

from deps_iam.domain.entities import PermissionEntity, RoleEntity
from deps_iam.domain.model import EntityId, Role

from .maga_user import EntityNameFactory
from .permission_entity import PermissionEntityFactory


class RoleEntityFactory(Factory):
    class Meta:
        model = RoleEntity

    pk = fuzzy.FuzzyInteger(1)
    name = fuzzy.FuzzyText()
    permissions: list[PermissionEntity] = LazyAttribute(lambda self: [PermissionEntityFactory() for _ in range(3)])


class RoleFactory(Factory):
    class Meta:
        model = Role

    group_id = LazyFunction(EntityId)
    name = SubFactory(EntityNameFactory)
