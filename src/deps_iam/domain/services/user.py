import uuid
from contextlib import suppress

from deps_iam.domain.dtos import ExpandedUser, UserListFilter, UserUpdateObject
from deps_iam.domain.entities import OrganisationPk
from deps_iam.domain.entities.user import UserEntity
from deps_iam.domain.exceptions import UserOrganisationAlreadyExistsError
from deps_iam.domain.interfaces.services import IUserService
from deps_iam.domain.services.customization_service import CustomizationService
from deps_iam.infrastructure.uow import UnitOfWork


class UserService(IUserService):
    def __init__(self, uow: UnitOfWork, customization_service: CustomizationService):
        self._uow = uow
        self._customization_service = customization_service

    def get(self, user_pk: str) -> UserEntity:
        with self._uow:
            return self._uow.user.get(user_pk)

    def get_expanded_user(self, user_pk: str) -> ExpandedUser:
        with self._uow:
            expanded_user = self._uow.user.get_expanded_user(user_pk)
        self._customization_service.enrich_customization_settings_for_user(expanded_user)
        return expanded_user

    def get_list(self, user_filter: UserListFilter = UserListFilter()) -> list[UserEntity]:
        with self._uow:
            return self._uow.user.get_list(user_filter)

    def add(self, user: UserEntity) -> UserEntity:
        with self._uow:
            res = self._uow.user.add(user)
            if user.organisation is not None and user.pk is not None:
                with suppress(UserOrganisationAlreadyExistsError):
                    self._uow.organisation.add_user_to_organisation(OrganisationPk(user.organisation), user_pk=user.pk)
            self._uow.commit()

        return res

    def update(self, user_pk: str, update_data: UserUpdateObject) -> UserEntity:
        with self._uow:
            res = self._uow.user.update(user_pk, update_data)
            self._uow.commit()

        return res

    def upsert(self, user: UserEntity) -> None:
        with self._uow:
            res = self._uow.user.upsert(user)
            self._uow.commit()

        return res

    def delete(self, user_pk: str) -> None:
        with self._uow:
            self._uow.user.delete(user_pk)
            self._uow.commit()

    def get_api_key(self, user_pk: str) -> str:
        with self._uow:
            return self._uow.user_api_key.get(user_pk)

    def get_user_by_api_key(self, api_key: str) -> UserEntity:
        with self._uow:
            user_pk = self._uow.user_api_key.get_user_by_api_key(api_key)
            return self._uow.user.get(user_pk)

    def delete_api_key(self, user_pk: str) -> None:
        with self._uow:
            self._uow.user_api_key.delete(user_pk)
            self._uow.commit()

    def create_api_key(self, user_pk: str) -> str:
        api_key = str(uuid.uuid4())
        with self._uow:
            res = self._uow.user_api_key.create(user_pk, api_key)
            self._uow.commit()

        return res

    def get_user_by_email(self, email: str) -> UserEntity:
        with self._uow:
            return self._uow.user.get_user_by_email(email)
