from factory import Factory, fuzzy
from faker import Faker
from pytest_factoryboy import register

from deps_iam.domain.entities import PermissionEntity

fake = Faker()


@register
class PermissionEntityFactory(Factory):
    class Meta:
        model = PermissionEntity

    name = fuzzy.FuzzyText()
