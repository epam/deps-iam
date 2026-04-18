import factory
from factory import Factory

from deps_iam.domain.model import (
    Action,
    Effect,
    EntityId,
    Policy,
    Principal,
    RequestStatement,
    Resource,
    Statement,
)


class ActionFactory(factory.Factory):
    class Meta:
        model = Action

    class Params:
        service = factory.Faker("word")
        action = factory.Faker("random_element", elements=["List", "Get", "Remove", "Create", "Update", "Run", "Add"])
        add_resource = factory.Faker("word")

    value = factory.LazyAttribute(lambda o: f"{o.service}:{o.action}{o.add_resource.capitalize()}")


class ResourceFactory(factory.Factory):
    class Meta:
        model = Resource

    class Params:
        service = factory.Faker("word")
        tenant = factory.Faker("word")
        something_else = factory.Faker("word")

    value = factory.LazyAttribute(lambda o: f"drn:{o.service}:{o.tenant}:{o.something_else}")


class PrincipalFactory(factory.Factory):
    class Meta:
        model = Principal

    class Params:
        faker_name = factory.Faker("name")

    value = factory.LazyAttribute(lambda o: o.faker_name.replace(" ", ","))


class StatementFactory(Factory):
    class Meta:
        model = Statement

    effect = factory.Faker("enum", enum_cls=Effect)
    actions = factory.List([factory.SubFactory(ActionFactory) for _ in range(5)])
    resources = factory.List([factory.SubFactory(ResourceFactory) for _ in range(5)])
    principals = factory.List([factory.SubFactory(PrincipalFactory) for _ in range(5)])


class PolicyFactory(Factory):
    class Meta:
        model = Policy

    class Params:
        uuid_faker = factory.Faker("uuid4")

    id_ = factory.LazyAttribute(lambda o: EntityId(str(o.uuid_faker)))
    statements = factory.List([factory.SubFactory(StatementFactory) for _ in range(5)])


class RequestStatementFactory(Factory):
    class Meta:
        model = RequestStatement

    action = factory.SubFactory(ActionFactory)
    resource = factory.SubFactory(ResourceFactory)
    principal = factory.SubFactory(PrincipalFactory)
