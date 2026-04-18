import random

import factory
import faker
from pytest_factoryboy import register

from deps_iam.domain.entities import Organisation

fake = faker.Faker()


@register
class OrganisationFactory(factory.Factory):
    class Meta:
        model = Organisation

    pk = factory.Faker("uuid4")
    name = factory.Faker("company")
    customization_url = factory.Iterator([None, fake.url()])
