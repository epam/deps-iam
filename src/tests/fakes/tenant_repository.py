from typing import Any

from deps_iam.domain.exceptions import TenantNotFoundError
from deps_iam.domain.model.tenant import ITenantRepository, Tenant


class FakeTenantRepository(ITenantRepository):
    def __init__(self):
        self._db: dict[str, Any] = {}

    def tenant_of_id(self, tenant_id: str) -> Tenant:
        if (tenant := self._db.get(tenant_id)) is not None:
            return tenant

        raise TenantNotFoundError(f"Tenant {tenant_id} not found")

    def save(self, tenant: Tenant) -> Tenant:
        self._db[tenant.id()] = tenant
        return tenant

    def delete(self, tenant: Tenant) -> None:
        self._db.pop(tenant.id(), None)
