import json

import pytest
from fastapi import FastAPI
from pytest_factoryboy import register
from starlette.testclient import TestClient

from deps_iam.api.middleware import cache
from deps_iam.app import create_fastapi, init_maga_application
from deps_iam.domain.model import Tenant, UserInfo
from deps_iam.infrastructure.access_management.context_vars import user
from tests.factories import (
    ActionFactory,
    EntityNameFactory,
    ExpandedUserFactory,
    GroupFactory,
    GroupInfoFactory,
    InvitationFactory,
    MagaUserFactory,
    OrganisationFactory,
    PermissionEntityFactory,
    PersonalInfoFactory,
    PolicyFactory,
    RequestStatementFactory,
    ResourceFactory,
    RoleEntityFactory,
    RoleFactory,
    TenantFactory,
    UserFactory,
    UserInfoFactory,
)


@pytest.fixture(scope="session")
def maga_app():
    yield init_maga_application()


@pytest.fixture
def maga_application(maga_app):
    maga_app.reset_singletons()
    yield maga_app


@pytest.fixture(scope="session")
def app() -> FastAPI:
    fastapi_app = create_fastapi()

    yield fastapi_app


@pytest.fixture(scope="session")
def application(app):
    yield app.app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def config(application):
    yield application.config


@pytest.fixture
def repositories(application):
    yield application.repositories


@pytest.fixture
def maga_repositories(maga_application):
    yield maga_application.repositories


@pytest.fixture
def services(application):
    yield application.services


@pytest.fixture
def maga_infrastructure_services(maga_application):
    yield maga_application.infrastructure_services


@pytest.fixture
def datasources(application):
    yield application.datasources


@pytest.fixture
def unit_of_works(application):
    yield application.unit_of_works


@pytest.fixture
def messaging(application):
    yield application.messaging


@pytest.fixture
def domain_event_publisher(application):
    yield application.domain_event_publisher()


@pytest.fixture
def get_role_dict():
    def func(role):
        permissions = [{"name": permission.name} for permission in role.permissions]
        return {
            "pk": role.pk,
            "name": role.name,
            "permissions": permissions,
        }

    return func


@pytest.fixture
def entity_based_token(user_entity):
    return json.dumps(
        {
            "subject": user_entity.pk,
            "roles": ["role"],
            "organisation": user_entity.organisation,
            "groups": ["group"],
            "email": user_entity.email,
            "first_name": user_entity.first_name,
            "last_name": user_entity.last_name,
        }
    )


@pytest.fixture(autouse=True)
def domain_service_access_managers(application):
    yield application.domain_service_access_managers


@pytest.fixture(autouse=True)
def domain_services_accessor(application):
    yield application.domain_service_accessors


@pytest.fixture
def other_organisation_user():
    return dict(
        subject="Other_DEPS",
        token="other_token",
        roles=["tester"],
        groups=["other_org"],
        email="other_email@epam.com",
        organisation="other_best_manufacture",
        first_name="Beps",
        last_name="B",
    )


@pytest.fixture
def this_user():
    return dict(
        subject="Deps",
        groups=["Deps_organisation_name"],
        token="token",
        roles=["tester"],
        email="tester_email@epam.com",
        organisation="Deps_org",
        first_name="Deps",
        last_name="D",
    )


@pytest.fixture(autouse=True)
def set_this_user(this_user):
    user.set(this_user)


@pytest.fixture(autouse=True)
def mock_cache_middleware(monkeypatch, mocker):
    monkeypatch.setattr(cache.CacheMiddleware, "_get_response_handler", mocker.Mock(return_value=None))


@pytest.fixture
def domain_tenant(tenant: Tenant):
    return tenant


@pytest.fixture
def domain_group(domain_tenant: Tenant):
    return domain_tenant.create_group("Domain group")


@pytest.fixture
def domain_user(domain_tenant: Tenant, user_info: UserInfo):
    return domain_tenant.create_user(user_info)


register(UserFactory)
register(ExpandedUserFactory)
register(PermissionEntityFactory)
register(OrganisationFactory)
register(RoleEntityFactory)
register(InvitationFactory)
register(ResourceFactory)
register(PolicyFactory)
register(UserInfoFactory)
register(RequestStatementFactory)
register(ActionFactory)
register(GroupFactory)
register(TenantFactory)
register(EntityNameFactory)
register(GroupInfoFactory)
register(PersonalInfoFactory)
register(MagaUserFactory, _name="maga_user")
register(RoleFactory)
