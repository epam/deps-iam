import os
from unittest import mock

import pytest
from deps_message_flow.sagas.orchestration import SagaInstance, SerializedSagaData

from deps_iam.domain.entities import Organisation
from deps_iam.infrastructure.access_management.context_vars import user
from tests.fakes import FakeMessageProducer


@pytest.fixture(autouse=True)
def session(app):
    database = app.app.datasources.postgres_datasource()
    connection = database.get_connection()

    class TrapForThreadLocalConnections:
        """
        This class is used instead of threading.local in Database, for allowing connection transactions management
        """

        connection = None

    TrapForThreadLocalConnections.connection = connection
    connection.begin()
    transaction = connection.begin_nested()
    database._registry = TrapForThreadLocalConnections
    try:
        yield
    finally:
        transaction.rollback()
    database.close()


@pytest.fixture
def permission_entity_repository(repositories):
    yield repositories.permission()


@pytest.fixture
def user_repository(repositories):
    yield repositories().user()


@pytest.fixture
def users_service(services):
    yield services().user()


@pytest.fixture
def organisation_repository(repositories):
    yield repositories.organisation()


@pytest.fixture
def organisation_service(services):
    yield services.organisation()


@pytest.fixture
def initialization_service(services):
    yield services.initialization()


@pytest.fixture(scope="class")
def envs_for_initialization():
    with mock.patch.dict(
        os.environ,
        {
            "SETUP_TENANT": "tenant1",
            "SETUP_USERS_INVITES_PATH": "/app/tests/data/users_for_invites.json",
        },
    ):
        yield


@pytest.fixture
def existing_organisation(organisation_repository, organisation):
    return organisation_repository.create(organisation)


@pytest.fixture
def role_repository(repositories):
    return repositories.role()


@pytest.fixture
def user_api_key_repository(repositories):
    return repositories.user_api_key()


@pytest.fixture
def existing_role(repositories, role_entity):
    def func(role=None, permissions=True, organisations=["deps-users", "test", "test1"]):
        role = role or role_entity
        if permissions:
            for permission in role.permissions:
                repositories.permission().add(permission),
        if organisations:
            for organisation in organisations:
                repositories.organisation().create(Organisation(pk=organisation, name=organisation))
        return role

    return func


@pytest.fixture
def existing_user(user_repository, client, user_entity):
    return user_repository.add(user_entity)


@pytest.fixture
def uow(unit_of_works):
    yield unit_of_works.uow()


@pytest.fixture
def produced_messages():
    yield []


@pytest.fixture(autouse=True)
def fake_message_producer(application, messaging, produced_messages):
    fake_producer = FakeMessageProducer(produced_messages)

    with messaging.true_producer.override(fake_producer):
        application.reset_singletons()
        yield fake_producer


@pytest.fixture
def set_existing_user(existing_user):
    user.set(
        dict(
            subject=existing_user.pk,
            token="token",
            groups=["def"],
            organisation="def",
            email="my_email@epam.com",
        )
    )


@pytest.fixture
def add_user_to_organisation(organisation_repository, existing_organisation, existing_user):
    existing_user.organisation = existing_organisation.pk
    organisation_repository.add_user_to_organisation(existing_organisation.pk, existing_user.pk)


@pytest.fixture
def create_approval_request(organisation_repository, existing_organisation, existing_user):
    return organisation_repository.create_approval_request(existing_organisation.pk, existing_user.pk)


@pytest.fixture(autouse=True)
def auth_mock(services, mocker):
    mock = mocker.Mock(services.authorization.cls)
    with services.authorization.override(mock):
        yield services.authorization()
    services.authorization.reset_override()


@pytest.fixture
def add_users_to_organisation(user_repository, organisation_repository, existing_organisation, user_factory):
    user1 = user_factory(pk="1", first_name="Test", last_name="Test")
    user2 = user_factory(pk="2", first_name="User", last_name="Some")
    user3 = user_factory(pk="3", first_name="User", last_name="Other")

    organisation_users = [user1, user2, user3]
    for user in organisation_users:
        user_repository.add(user)
        organisation_repository.add_user_to_organisation(existing_organisation.pk, user.pk)


@pytest.fixture
def saga_instance_repo(repositories):
    yield repositories.saga_instance()


@pytest.fixture
def serialized_saga_data():
    return SerializedSagaData(saga_data_type="TestData", saga_data_json="{'test': true}")


@pytest.fixture
def saga_instance(serialized_saga_data):
    return SagaInstance(
        saga_type="Test",
        saga_id="None",
        state_name="????",
        last_request_id="None",
        serialized_saga_data=serialized_saga_data,
    )
