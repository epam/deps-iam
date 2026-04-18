from .base import AlreadyExistsError, NotFoundError


class PermissionAlreadyExistsError(AlreadyExistsError):
    code = "permission_already_exists"


class PermissionNotFoundError(NotFoundError):
    code = "permission_not_found_error"
