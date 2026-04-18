import factory

from deps_iam.domain.model import Email, EntityId, UserInfo


class UserInfoFactory(factory.Factory):
    class Meta:
        model = UserInfo

    class Params:
        user_info_id_ = factory.Faker("uuid4")
        user_email = factory.Faker("email")

    id_ = factory.LazyAttribute(lambda o: EntityId(o.user_info_id_))
    first_name = factory.Faker("name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda o: Email(o.user_email))
