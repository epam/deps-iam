from abc import ABC, abstractmethod

from deps_iam.domain.model.tenant import Tenant

__all__ = ["ITenantRepository"]


class ITenantRepository(ABC):
    @abstractmethod
    def tenant_of_id(self, tenant_id: str) -> Tenant:
        pass
