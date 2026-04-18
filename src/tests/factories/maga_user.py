import factory

from deps_iam.domain.model import (
    Email,
    EntityId,
    EntityName,
    GroupInfo,
    PersonalInfo,
    User,
)

__all__ = ["EntityNameFactory", "GroupInfoFactory", "PersonalInfoFactory", "MagaUserFactory"]


class EntityNameFactory(factory.Factory):
    class Meta:
        model = EntityName

    class Params:
        service = factory.Faker("word")
        tenant = factory.Faker("word")
        something_else = factory.Faker(
            "random_element", elements=["List", "Get", "Remove", "Create", "Update", "Run", "Add"]
        )

    name = factory.Faker("word")
    drn = factory.LazyAttribute(lambda o: f"drn:{o.service}:{o.tenant}:{o.something_else}")


class GroupInfoFactory(factory.Factory):
    class Meta:
        model = GroupInfo

    group = factory.SubFactory(EntityNameFactory)
    role = factory.SubFactory(EntityNameFactory)


class PersonalInfoFactory(factory.Factory):
    class Meta:
        model = PersonalInfo

    class Params:
        fake_email = factory.Faker("email")

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda o: Email(o.fake_email))


class MagaUserFactory(factory.Factory):
    class Meta:
        model = User

    id_ = factory.LazyFunction(EntityId)
    tenant_id = factory.LazyFunction(EntityId)
    personal_info = factory.SubFactory(PersonalInfoFactory)
