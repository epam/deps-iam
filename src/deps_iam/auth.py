import json

from fastapi.requests import Request

from deps_iam.domain.exceptions import AuthError
from deps_iam.infrastructure.access_management.context_vars import user

PUBLIC_ENDPOINTS = {  # noqa: WPS407
    "/api/iam/v1/docs": ("GET",),
    "/api/iam/v1/docs/swagger-ui.css": ("GET",),
    "/api/iam/v1/openapi.json": ("GET",),
    "/api/iam/healthcheck": ("GET",),
    "/api/iam/service-info/version": ("GET",),
    "/api/iam/debug/500": ("GET",),
    "/favicon.ico": ("GET",),
    "/api/iam/v1/authorize": ("GET",),
    "/api/iam/v1/users": ("POST",),
    "/api/iam/v2/authorize": ("POST",),
}


def set_user_from_deps_token(request: Request) -> None:
    if not path_is_public(request):
        try:
            deps_token = json.loads(request.headers["deps-token"])
            validate_deps_token(deps_token)
            deps_token["deps_token"] = request.headers["deps-token"]
            user.set(deps_token)
        except KeyError:
            raise AuthError("Deps-token doesn't provided.")
        except TypeError:
            raise AuthError("Provided deps-token isn't correct.")


def validate_deps_token(deps_token: str) -> None:
    if not deps_token:
        raise AuthError("Deps-token doesn't provided.")


def path_is_public(request):
    return request.url.path in PUBLIC_ENDPOINTS and request.method in PUBLIC_ENDPOINTS[request.url.path]
