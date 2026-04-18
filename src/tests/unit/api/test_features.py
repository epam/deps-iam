from http import HTTPStatus

import pytest

from tests.endpoints import CUSTOMIZATION_SETTINGS_ENDPOINT


# Tests different endpoints for default behaviour
@pytest.mark.customization_settings
def test_organization_settings__default_does_not_enabled__not_found(client, config):
    res = client.get(CUSTOMIZATION_SETTINGS_ENDPOINT)
    assert res.status_code == HTTPStatus.NOT_FOUND
