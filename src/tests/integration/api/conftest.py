import pytest

from deps_iam import auth


@pytest.fixture(autouse=True)
def mocked_middleware(monkeypatch, mocker):
    monkeypatch.setattr(auth, "set_user_from_deps_token", mocker.Mock({}))
