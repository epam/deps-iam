from .base import NotFoundError


class TenantNotFoundError(NotFoundError):
    code = "tenant_not_found"
