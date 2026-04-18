import http

from deps_iam.domain.exceptions import IAMException


class RegisterError(IAMException):
    code = "registration_error"

    def __init__(self, detail: str, status_code: int = http.HTTPStatus.BAD_REQUEST):
        super().__init__(detail)
        self.status_code = status_code
