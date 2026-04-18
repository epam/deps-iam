from datetime import timezone

import factory
from pytest_factoryboy import register

from deps_iam.domain.dtos import ExpandedUser, ListDataObject
from deps_iam.domain.entities.user import UserEntity
from tests.factories import OrganisationFactory
from tests.factories.common import ListMetaDataFactory


class UserFactory(factory.Factory):
    class Meta:
        model = UserEntity

    pk = factory.Faker("uuid4")
    created_at = factory.Faker("date_time", tzinfo=timezone.utc)
    username = factory.Faker("ascii_email")
    email = factory.Faker("ascii_email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    organisation = None


class ExpandedUserFactory(UserFactory):
    class Meta:
        model = ExpandedUser

    organisation = factory.Iterator([OrganisationFactory()])


@register
class UserListDataFactory(factory.Factory):
    class Meta:
        model = ListDataObject

    meta = factory.SubFactory(ListMetaDataFactory)
    result = factory.LazyAttribute(lambda self: [UserFactory() for _ in range(self.meta.size)])
