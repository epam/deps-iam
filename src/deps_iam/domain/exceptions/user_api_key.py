from .base import NotFoundError


class UserApiKeyNotFoundError(NotFoundError):
    code = "user_api_key_not_found"
