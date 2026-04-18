import pytest

from deps_iam.application import UserService
from deps_iam.domain.model import IUserRepository
from deps_iam.infrastructure.services.identity_provider.exceptions import (
    AccessTokenAuthServiceError,
)


@pytest.mark.sign_in
def test_sign_in__user_doesnt_exist__false(
    user_service: UserService,
    test_token,
):
    is_user_signed_up = user_service.sign_in(access_token=test_token)

    assert is_user_signed_up == False


@pytest.mark.sign_in
def test_sign_in__user_exists__true(
    user_service: UserService,
    fake_maga_user_repository: IUserRepository,
    test_token,
    test_user_info,
    maga_user_factory,
):
    user = maga_user_factory(id_=test_user_info.id)
    fake_maga_user_repository.save(user)

    is_user_signed_up = user_service.sign_in(access_token=test_token)

    assert is_user_signed_up == True


@pytest.mark.sign_in
def test_sign_in__wrong_token__error(user_service: UserService):
    with pytest.raises(AccessTokenAuthServiceError):
        user_service.sign_in(access_token="wrong_token")
