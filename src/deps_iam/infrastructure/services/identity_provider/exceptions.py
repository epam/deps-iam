from deps_iam.domain.exceptions import IAMException


class AccessTokenAuthServiceError(IAMException):
    code = "authentication_error"
