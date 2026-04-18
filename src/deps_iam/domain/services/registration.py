import contextlib
import datetime
import logging
import re
from typing import Any, Dict

from deps_iam import constants
from deps_iam.domain.entities import Organisation, OrganisationPk, UserEntity
from deps_iam.domain.exceptions import OrganisationAlreadyExistsError, RegisterError
from deps_iam.domain.services.organisation import OrganisationService
from deps_iam.domain.services.user import UserService
from deps_iam.infrastructure.uow import UnitOfWork

logger = logging.getLogger(__name__)

EMAIL_PATTERN = r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b"


class RegistrationService:
    def __init__(
        self,
        uow: UnitOfWork,
        org_service: OrganisationService,
        user_service: UserService,
    ):
        self._uow = uow
        self._org_service = org_service
        self._user_service = user_service

    def register_user(self, user_credentials: Dict[str, Any], is_personal: bool):
        self._validate_userinfo(user_credentials)

        with self._uow:
            user_obj = self._generate_new_user(user_credentials)
            self._user_service.add(user_obj)
            if user_credentials.get("organisation"):
                self.create_activate_new_user_organisation(user_credentials, user_obj.pk, is_personal)
            self._uow.commit()
        logger.info(f"New user with email: {user_credentials['email']} registered.")

    def create_activate_new_user_organisation(
        self,
        user_credentials: dict[str, Any],
        user_pk: str,
        is_org_personal: bool = False,
    ) -> None:
        organisation = self.generate_organisation(user_credentials, is_org_personal)
        with self._uow:
            self._create_org_if_does_not_exist(organisation)
            self._org_service.add_user_to_organisation(organisation.pk, user_pk)
            self._org_service.activate_user_organisation(organisation.pk, user_pk)
            self._uow.commit()

    def _create_org_if_does_not_exist(self, organisation: Organisation) -> None:
        with contextlib.suppress(OrganisationAlreadyExistsError):
            self._org_service.create_organisation(organisation)

    def generate_organisation(
        self,
        user_credentials: dict[str, Any],
        is_personal: bool = False,
    ) -> Organisation:
        org_name = self._generate_org_name(user_credentials) if is_personal else user_credentials["organisation"]
        return Organisation(
            pk=OrganisationPk(user_credentials["organisation"]),
            name=org_name,
            is_personal=is_personal,
        )

    @staticmethod
    def _generate_org_name(user: dict[str, Any]) -> str:
        first_name = user.get("first_name")
        last_name = user.get("last_name")
        if first_name and last_name:
            return f"{first_name} {last_name} {constants.PERSONAL_ORGANISATION_POSTFIX}"
        return f"{user.get('email')} {constants.PERSONAL_ORGANISATION_POSTFIX}"

    @staticmethod
    def _generate_new_user(user_credentials: dict) -> UserEntity:
        return UserEntity(
            pk=user_credentials["subject"],
            created_at=datetime.datetime.utcnow(),
            username=user_credentials["email"],
            email=user_credentials["email"],
            first_name=user_credentials["first_name"],
            last_name=user_credentials["last_name"],
            organisation=None,
        )

    @staticmethod
    def _validate_userinfo(userinfo: Dict[str, Any]) -> None:
        if not userinfo.get("email"):
            raise RegisterError(
                "Email not provided in userinfo. Add email in your profile or extend scope for client in oidc provider."
            )
        if not re.match(EMAIL_PATTERN, userinfo["email"]):
            raise RegisterError("Email invalid.")
