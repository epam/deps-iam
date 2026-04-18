import factory

from deps_iam.domain.model import EntityId, Tenant


class TenantFactory(factory.Factory):
    class Meta:
        model = Tenant

    id_ = factory.LazyFunction(EntityId)
    name = factory.Faker("company")
