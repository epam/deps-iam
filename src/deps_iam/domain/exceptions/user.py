from deps_iam.domain.exceptions.base import (
    AlreadyExistsError,
    ForbiddenError,
    NotFoundError,
)


class UserNotFoundError(NotFoundError):
    code = "user_not_found_error"


class UserAlreadyExistsError(AlreadyExistsError):
    code = "user_already_exists_error"


class UserForbiddenError(ForbiddenError):
    code = "user_forbidden_error"
