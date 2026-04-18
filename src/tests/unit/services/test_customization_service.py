import pytest

from tests.factories import OrganisationFactory


@pytest.fixture
def customization_service(services):
    services.customization.reset_override()
    yield services.customization()


def test_customization_service__customization_default_customization_enriched(
    customization_service, expanded_user, config
):
    expanded_user.default_customization_service = None
    customization_service.enrich_customization_settings_for_user(expanded_user)

    assert expanded_user.default_customization_url == config.default_customization_url()
