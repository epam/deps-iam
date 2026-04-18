from typing import Callable

from deps_iam.domain.dtos import OrganisationListFilter
from deps_iam.domain.entities.organisation import OrganisationPk
from deps_iam.domain.exceptions import OrganisationForbiddenError
from deps_iam.domain.interfaces.access_managers import IOrganisationAccessManager
from deps_iam.extras.interfaces import IUoW
from deps_iam.infrastructure.access_management.access_managers.user import (
    CurrentUserMixin,
)


class OrganisationAccessManager(IOrganisationAccessManager, CurrentUserMixin):
    def __init__(self, uow: Callable[..., IUoW]) -> None:
        self._uow = uow

    def check_access(self, organisation_pk: OrganisationPk) -> None:
        with self._uow:  # type: ignore
            user_organisation_pks = {
                org.pk
                for org in self._uow.organisation.get_list(  # type: ignore
                    OrganisationListFilter(user_pk=self.current_user.subject)
                )
            }
        if organisation_pk not in user_organisation_pks:
            raise OrganisationForbiddenError(f"User hasn't access to organisation: {organisation_pk}")

    def grant_access(self, organisation_pk: OrganisationPk) -> None:
        with self._uow:  # type: ignore
            self._uow.organisation.add_user_to_organisation(organisation_pk, self.current_user.subject)  # type: ignore
            self._uow.commit()  # type: ignore

    def patch_filter(self, filtering: OrganisationListFilter) -> None:
        filtering.user_pk = self.current_user.subject
