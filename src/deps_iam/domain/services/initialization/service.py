import json
import logging
from datetime import datetime
from uuid import uuid4

from deps_iam.domain.dtos import UserListFilter, UserUpdateObject
from deps_iam.domain.entities import Organisation, UserEntity
from deps_iam.domain.model import UserData
from deps_iam.domain.services.organisation import OrganisationService
from deps_iam.domain.services.user import UserService

from .settings import Settings

__all__ = ["InitializationService"]


class InitializationService:
    def __init__(
        self,
        organisation_service: OrganisationService,
        user_service: UserService,
    ) -> None:
        self._settings = Settings()
        self._organisation_service = organisation_service
        self._user_service = user_service

        self._logger = logging.getLogger(self.__class__.__name__)

    def create_tenant_with_users(self) -> None:
        users_to_invite: list[UserData] = self._get_users_to_invite()
        tenant = self._create_tenant()

        for user_to_invite in users_to_invite:
            user_to_invite["organisation"] = tenant.pk

        users_to_invite_by_emails = {user["email"]: user for user in users_to_invite}

        existing_users = self._get_existing_users(users_to_invite)
        existing_users_emails = {user.email for user in existing_users}

        users_to_create = self._get_users_to_create(users_to_invite_by_emails, existing_users_emails)

        self._create_users(users_to_create)
        self._update_users(users_to_invite_by_emails, users_to_update=existing_users)

    def _create_tenant(self) -> Organisation:
        return self._organisation_service.create_organisation(Organisation(name=self._settings.tenant))

    def _create_users(self, new_users: list[UserData]) -> None:
        for user in new_users:
            user_entity = UserEntity(**user, pk=str(uuid4()), created_at=datetime.utcnow())
            self._user_service.add(user_entity)

    def _update_users(self, users_to_invite_by_emails: dict[str, UserData], users_to_update: list[UserEntity]) -> None:
        for user_to_update in users_to_update:
            user_to_invite = users_to_invite_by_emails[user_to_update.email]
            self._user_service.update(
                user_pk=user_to_update.pk,
                update_data=UserUpdateObject(
                    first_name=user_to_invite["first_name"],
                    last_name=user_to_invite["last_name"],
                    organisation=user_to_invite["organisation"],
                ),
            )

    def _get_users_to_invite(self) -> list[UserData]:
        with open(f"{self._settings.users_invites_path}") as file:
            users_invites = json.loads(file.read())

        return [
            UserData(first_name=user["firstName"], last_name=user["lastName"], email=user["email"])
            for user in users_invites
        ]

    def _get_users_to_create(
        self,
        users_to_invite_by_emails: dict[str, UserData],
        existing_users_emails: set[str],
    ) -> list[UserData]:
        user_emails_to_create = set(users_to_invite_by_emails.keys()).difference(existing_users_emails)
        return [user for user_email, user in users_to_invite_by_emails.items() if user_email in user_emails_to_create]

    def _get_existing_users(self, users_to_invite: list[UserData]) -> list[UserEntity]:
        users_emails = [user["email"] for user in users_to_invite]

        return self._user_service.get_list(
            user_filter=UserListFilter(emails=users_emails),
        )
