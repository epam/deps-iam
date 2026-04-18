class IAMException(Exception):
    code = "iam_exception"


class NotFoundError(IAMException):
    code = "not_found_error"


class AlreadyExistsError(IAMException):
    code = "already_exists_error"


class ForbiddenError(IAMException):
    code = "forbidden_error"
