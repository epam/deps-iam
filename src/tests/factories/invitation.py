import factory
from pytest_factoryboy import register

from deps_iam.domain.entities import Invitation


@register
class InvitationFactory(factory.Factory):
    class Meta:
        model = Invitation

    email = factory.Faker("ascii_email")
