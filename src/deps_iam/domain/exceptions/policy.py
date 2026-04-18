from .base import AlreadyExistsError, NotFoundError


class PolicyNotFoundError(NotFoundError):
    code = "policy_not_found"


class PolicyAlreadyExistsError(AlreadyExistsError):
    code = "policy_already_exists"
