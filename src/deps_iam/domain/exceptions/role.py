from .base import AlreadyExistsError, NotFoundError


class RoleNotFoundError(NotFoundError):
    code = "role_not_found"


class RoleAlreadyExistsError(AlreadyExistsError):
    code = "role_already_exists"
