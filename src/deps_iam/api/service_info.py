from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_iam.api.models.build_info import BuildInfoModel
from deps_iam.containers import Core

from .endpoint_marker import MarkerRoute
from .endpoint_visibility import Visibility

service_info_router = APIRouter(prefix="/service-info", route_class=MarkerRoute)


@service_info_router.get(
    "/version",
    tags=["Service Info"],
    response_model=BuildInfoModel,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_build_info(build_info=Depends(Provide[Core.build_info])):
    return BuildInfoModel(**build_info)
