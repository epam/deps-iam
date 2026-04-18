from typing import Any, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Request, Response

from deps_iam.containers import Services
from deps_iam.domain.services.authorization import AuthorizationService

from ..endpoint_marker import MarkerRoute
from ..endpoint_visibility import Visibility

authorization_router = APIRouter(prefix="/authorize", tags=["Authorization"], route_class=MarkerRoute)


@authorization_router.post(
    "",
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def authorize(
    request: Request,
    response: Response,
    body: Optional[Any] = Body(...),
    authorization_service: AuthorizationService = Depends(Provide[Services.authorization]),
):
    deps_token = authorization_service.authorize(request.headers)
    response.headers["deps-token"] = deps_token
    return {"deps-token": deps_token}
