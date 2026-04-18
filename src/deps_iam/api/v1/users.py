from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, Response

from deps_iam.api.models.dtos import (
    UserCreateModel,
    UserListFilterModel,
    UserUpdateObjectModel,
)
from deps_iam.api.models.user import ExpandedUserModel, UserModel
from deps_iam.constants import API_KEY
from deps_iam.containers import InfrastructureServices, Services
from deps_iam.domain.services.user import UserService
from deps_iam.extras.auth.deps_auth import DepsAuthService

from ..endpoint_marker import MarkerRoute
from ..endpoint_visibility import Visibility

users_router = APIRouter(prefix="/users", tags=["Users"], route_class=MarkerRoute)


@users_router.get(
    "/me",
    response_model=ExpandedUserModel,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_current_user(
    request: Request,
    auth_service: DepsAuthService = Depends(Provide[InfrastructureServices.deps_auth_service]),
    user_service: UserService = Depends(Provide[Services.user]),
):
    credentials = auth_service.authorize(request.headers)
    user_pk = credentials["subject"]

    return ExpandedUserModel.model_validate(user_service.get_expanded_user(user_pk=user_pk))


@users_router.get(
    "/{user_pk}",
    response_model=UserModel,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_user_detail(
    user_pk: str,
    user_service: UserService = Depends(Provide[Services.user]),
):
    return UserModel.model_validate(user_service.get(user_pk=user_pk))


@users_router.delete(
    "/{user_pk}",
    response_model=bool,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_user(
    user_pk: str,
    user_service: UserService = Depends(Provide[Services.user]),
):
    user_service.delete(user_pk)
    return True


@users_router.patch(
    "/{user_pk}",
    response_model=UserModel,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def update_user(
    user_pk: str,
    user_data: UserUpdateObjectModel,
    user_service: UserService = Depends(Provide[Services.user]),
):
    return user_service.update(user_pk, user_data.to_domain())


@users_router.get(
    "",
    response_model=list[UserModel],
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_users_list(  # noqa: WPS234
    filtering: UserListFilterModel = UserListFilterModel(),
    user_service: UserService = Depends(Provide[Services.user]),
):
    users = user_service.get_list(filtering.to_domain())
    return [UserModel.model_validate(user) for user in users]


@users_router.get(
    "/me/api-key",
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_user_api_key(
    request: Request,
    user_service: UserService = Depends(Provide[Services.user]),
):
    user_pk = _get_current_user_pk(request)

    return user_service.get_api_key(user_pk)


@users_router.delete(
    "/me/api-key",
    status_code=HTTPStatus.NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_user_api_key(
    request: Request,
    user_service: UserService = Depends(Provide[Services.user]),
):
    user_pk = _get_current_user_pk(request)

    return user_service.delete_api_key(user_pk)


@users_router.post(
    "/me/api-key/generate",
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def generate_user_api_key(
    request: Request,
    user_service: UserService = Depends(Provide[Services.user]),
):
    user_pk = _get_current_user_pk(request)

    return user_service.create_api_key(user_pk)


@users_router.post(
    "",
    response_model=UserModel,
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def create_user(
    response: Response,
    user: UserCreateModel,
    create_api_key: bool = Body(default=False, alias="createAPIKey"),
    user_service: UserService = Depends(Provide[Services.user]),
):
    new_user = user_service.add(user.to_domain())

    if create_api_key:
        response.headers[API_KEY] = user_service.create_api_key(new_user.pk)

    return UserModel.model_validate(new_user)


@inject
def _get_current_user_pk(
    request: Request,
    auth_service: DepsAuthService = Depends(Provide[InfrastructureServices.deps_auth_service]),
) -> str:
    credentials = auth_service.authorize(request.headers)
    return credentials["subject"]
