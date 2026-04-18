from contextlib import ExitStack
from copy import deepcopy
from uuid import uuid4

import pytest
from dependency_injector.providers import Configuration, DependenciesContainer, Self

from deps_iam.application import GroupService
from deps_iam.domain.model import EntityId, Group, GroupInfo, PersonalInfo, Tenant
from tests.fakes import (
    FakeConnectionProvider,
    FakeIdentityProvider,
    FakePolicyRepository,
    FakeUserRepository,
)

DO_NOT_OVERRIDE_OBJS = (Self, DependenciesContainer, Configuration)


@pytest.fixture(autouse=True)
def repositories(application, repositories, mocker):
    with ExitStack() as context:
        for repository_provider in repositories.providers.values():
            if isinstance(repository_provider, DO_NOT_OVERRIDE_OBJS):
                continue

            context.enter_context(repository_provider.override(mocker.Mock(repository_provider.cls)))

        application.reset_singletons()
        yield repositories

    application.reset_singletons()


@pytest.fixture(autouse=True)
def services(application, services, mocker):
    mocked_services = []
    for service_provider in services.providers.values():
        if isinstance(service_provider, DO_NOT_OVERRIDE_OBJS):
            continue

        service_provider.override(mocker.Mock(service_provider.cls))
        mocked_services.append(service_provider)

    application.reset_singletons()
    yield services

    for service_provider in mocked_services:
        service_provider.reset_override()
    application.reset_singletons()


@pytest.fixture
def postgres_datasource_mock(mocker, datasources):
    mock = mocker.Mock(datasources.postgres_datasource())
    with datasources.postgres_datasource.override(mock):
        yield mock


@pytest.fixture
def organisation_repository_mock(repositories):
    yield repositories.organisation()


@pytest.fixture
def permission_repository_mock(repositories):
    yield repositories.permission()


@pytest.fixture
def role_repository_mock(repositories):
    yield repositories.role()


@pytest.fixture
def user_repository_mock(repositories):
    yield repositories.user()


@pytest.fixture
def user_api_key_repository_mock(repositories):
    yield repositories.user_api_key()


@pytest.fixture
def fake_maga_user_repository(maga_repositories):
    with maga_repositories.user.override(FakeUserRepository()):
        yield maga_repositories.user()


@pytest.fixture
def fake_policy_repository(maga_repositories):
    with maga_repositories.policy.override(FakePolicyRepository()):
        yield maga_repositories.policy()


@pytest.fixture
def fake_group_repository(maga_repositories):
    return maga_repositories.group()


@pytest.fixture
def maga_services(maga_application):
    return maga_application.services()


@pytest.fixture
def maga_group_service(maga_services):
    return maga_services.group()


@pytest.fixture
def maga_policy_service(maga_services, fake_policy_repository):
    return maga_services.policy()


@pytest.fixture
def maga_user_service(maga_services, fake_maga_user_repository):
    return maga_services.user()


@pytest.fixture
def organisation_service_mock(services):
    yield services.organisation()


@pytest.fixture
def permission_service_mock(services):
    yield services.permission()


@pytest.fixture
def role_service_mock(services):
    yield services.role()


@pytest.fixture
def user_service_mock(services):
    yield services.user()


@pytest.fixture
def customization_service_mock(services):
    yield services.customization()


@pytest.fixture
def authorization_service_mock(services):
    yield services.authorization()


@pytest.fixture
def test_token():
    return uuid4().hex


@pytest.fixture
def test_user_info(user_info):
    return user_info


@pytest.fixture
def fake_identity_provider(maga_infrastructure_services, test_token, test_user_info):
    with maga_infrastructure_services.identity_provider.override(
        FakeIdentityProvider(identities={test_token: test_user_info})
    ):
        yield maga_infrastructure_services.identity_provider()


@pytest.fixture
def org_access_manager(domain_service_access_managers):
    return domain_service_access_managers.organisation()


@pytest.fixture
def org_services_accessor_mock(mocker, domain_services_accessor):
    mock = mocker.Mock(domain_services_accessor.organisation())
    with domain_services_accessor.organisation.override(mock):
        yield mock


@pytest.fixture(autouse=True)
def connection_provider(datasources, application):
    with datasources.connection_provider.override(FakeConnectionProvider()):
        application.reset_singletons()
        yield datasources.connection_provider()


@pytest.fixture
def fake_tenant_repository(maga_repositories):
    return maga_repositories.tenant()


@pytest.fixture
def test_tenant():
    return Tenant(id_=EntityId(), name="deps")


@pytest.fixture
def test_group(test_tenant):
    return Group(id_=EntityId(), tenant_id=test_tenant.id, name="deps-admins")


@pytest.fixture
def user_id_entity():
    return EntityId()


@pytest.fixture
def fake_user_repository(maga_repositories):
    return maga_repositories.user()


@pytest.fixture
def test_entity_name(entity_name_factory):
    return entity_name_factory()


@pytest.fixture
def existing_tenant(fake_tenant_repository, test_tenant):
    fake_tenant_repository._db[test_tenant.id()] = test_tenant
    return test_tenant


@pytest.fixture
def test_role(role_factory):
    return role_factory()


@pytest.fixture
def test_personal_group(existing_tenant, test_user_info):
    group = existing_tenant.create_group("SunPerMoon")
    group.accept(test_user_info.id)
    group.give_ownership(test_user_info.id)
    return group


@pytest.fixture
def existing_group(test_personal_group, fake_group_repository):
    fake_group_repository.save(deepcopy(test_personal_group))
    return test_personal_group


@pytest.fixture
def test_personal_info(test_user_info):
    return PersonalInfo(test_user_info.first_name, test_user_info.last_name, test_user_info.email)


@pytest.fixture
def test_group_info(test_group, test_role, entity_name_factory):
    return GroupInfo(
        group=entity_name_factory(name=test_group.name.name, drn=test_group.name.drn),
        role=entity_name_factory(name=test_role.name.name, drn=test_role.name.drn),
    )


@pytest.fixture
def existing_maga_user(existing_tenant, test_user_info, test_personal_group, fake_maga_user_repository):
    user = existing_tenant.create_user(test_user_info)
    user.join_group(test_personal_group)
    fake_maga_user_repository.save(user)
    return user
