from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_iam.api.models import RoleAddModel, RoleModel
from deps_iam.containers import Services
from deps_iam.domain.entities.role import RolePk
from deps_iam.domain.services import RoleService

from ..endpoint_marker import MarkerRoute
from ..endpoint_visibility import Visibility

roles_router = APIRouter(prefix="/roles", tags=["Roles"], route_class=MarkerRoute)


@roles_router.post(
    "",
    response_model=RoleModel,
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def create_role(
    role_model: RoleAddModel,
    role_service: RoleService = Depends(Provide[Services.role]),
):
    return role_service.create(role_model.to_domain())


@roles_router.get(
    "/{role_pk}",
    response_model=RoleModel,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_role(
    role_pk: RolePk,
    role_service: RoleService = Depends(Provide[Services.role]),
):
    return role_service.get(role_pk)


@roles_router.delete(
    "/{role_pk}",
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_role(
    role_pk: RolePk,
    role_service: RoleService = Depends(Provide[Services.role]),
):
    return role_service.delete(role_pk)


@roles_router.put(
    "/{role_pk}",
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def update_role(
    role_pk: RolePk,
    role_model: RoleAddModel,
    role_service: RoleService = Depends(Provide[Services.role]),
):
    return role_service.update(role_pk, role_model.to_domain())


@roles_router.get(
    "",
    response_model=list[RoleModel],
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_roles(
    role_service: RoleService = Depends(Provide[Services.role]),
):
    return role_service.get_list()
