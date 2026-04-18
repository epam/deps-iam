import factory
from faker import Faker
from pytest_factoryboy import register

from deps_iam.domain.dtos import ListMetaDataObject

fake = Faker()


@register
class ListMetaDataFactory(factory.Factory):
    class Meta:
        model = ListMetaDataObject

    total = fake.pyint(min_value=1, max_value=10)
    size = fake.pyint(min_value=1, max_value=total)
