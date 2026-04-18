from abc import ABC, abstractmethod

from deps_iam.domain.dtos import OrganisationListFilter
from deps_iam.domain.entities import OrganisationPk


class IOrganisationAccessManager(ABC):
    @abstractmethod
    def check_access(self, organisation_pk: OrganisationPk) -> None:
        ...

    @abstractmethod
    def grant_access(self, organisation_pk: OrganisationPk) -> None:
        ...

    @abstractmethod
    def patch_filter(self, org_filtering: OrganisationListFilter) -> None:
        ...
