from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

from deps_iam.containers import Datasources
from deps_iam.extras.datasource import Database

from .endpoint_marker import MarkerRoute
from .endpoint_visibility import Visibility

healthcheck_router = APIRouter(route_class=MarkerRoute)


@healthcheck_router.get(
    "/healthcheck",
    tags=["Debug"],
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def service_healthcheck(datasource: Database = Depends(Provide[Datasources.postgres_datasource])):
    """check connection to database"""
    try:
        datasource.healthcheck()
    except Exception:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(status_code=status.HTTP_200_OK)
