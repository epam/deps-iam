from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_iam.containers import Services
from deps_iam.domain.services.permission import PermissionService

from ..endpoint_marker import MarkerRoute
from ..endpoint_visibility import Visibility

permissions_router = APIRouter(prefix="/permissions", tags=["Permissions"], route_class=MarkerRoute)


@permissions_router.get(
    "",
    response_model=list[str],
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_list_permissions(
    permission_service: PermissionService = Depends(Provide[Services.permission]),
) -> list[str]:
    return [entity.name for entity in permission_service.get_list()]
