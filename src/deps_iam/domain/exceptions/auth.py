import http

from .base import IAMException


class AuthError(IAMException):
    code = "authentication_error"

    def __init__(self, detail: str, status_code: int = http.HTTPStatus.UNAUTHORIZED):
        super().__init__(detail)
        self.status_code = status_code


class AccessTokenAuthServiceError(IAMException):
    code = "authentication_error"
