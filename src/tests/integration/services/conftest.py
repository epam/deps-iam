import pytest


@pytest.fixture
def authorization_service(services):
    yield services.authorization()


@pytest.fixture
def use_enable_personal_org(application, config):
    with config.authentication.enable_personal_org.override(True):
        application.reset_singletons()
        yield


@pytest.fixture
def use_api_key_auth_enabled(application, config):
    with config.authentication.api_key_auth_enabled.override(True):
        application.reset_singletons()
        yield
