import json
import os

import pytest

from deps_iam.constants import PERSONAL_ORGANISATION_POSTFIX
from deps_iam.domain.dtos import (
    OrganisationListFilter,
    OrganisationTypesEnum,
    OrganisationUpdate,
    UserListFilter,
)
from deps_iam.domain.exceptions import (
    ApprovalRequestNotFoundError,
    InvitationNotFoundError,
    OrganisationAlreadyExistsError,
    OrganisationForbiddenError,
    OrganisationNotFoundError,
    UserOrganisationAlreadyExistsError,
    UserOrganisationNotFoundError,
)
from deps_iam.domain.model import UserData
from deps_iam.domain.services import InitializationService, OrganisationService
from tests.factories import UserFactory


class TestInitializationService:
    def test_create_tenant_with_users__tenant_created(
        self,
        initialization_service: InitializationService,
        organisation_service: OrganisationService,
        envs_for_initialization,
        produced_messages,
    ) -> None:
        initialization_service.create_tenant_with_users()
        created_tenant = organisation_service.get_organisation_by_name(os.environ["SETUP_TENANT"])

        assert len(produced_messages) == 2
        assert created_tenant.name == os.environ["SETUP_TENANT"]

    def test_create_tenant_with_users__users_added_to_tenant(
        self,
        initialization_service: InitializationService,
        organisation_service: OrganisationService,
        envs_for_initialization,
        produced_messages,
    ) -> None:
        initialization_service.create_tenant_with_users()
        created_tenant = organisation_service.get_organisation_by_name(os.environ["SETUP_TENANT"])

        users_to_invite = self._get_users_to_invite()

        organisation_users = organisation_service.get_organisation_users(
            pk=created_tenant.pk, filtering=UserListFilter()
        )

        assert len(users_to_invite) == len(organisation_users.result)

    def _get_users_to_invite(self) -> list[UserData]:
        with open(f"{os.environ['SETUP_USERS_INVITES_PATH']}") as file:
            users_invites = json.loads(file.read())

        return [
            UserData(first_name=user["firstName"], last_name=user["lastName"], email=user["email"])
            for user in users_invites
        ]
