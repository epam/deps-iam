from datetime import datetime

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_serializer

from deps_iam.api.models.organisation import OrganisationModel
from deps_iam.domain.dtos import UserListFilter, UserSortingFieldsEnum
from deps_iam.domain.entities.user import UserEntity


class UserModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    pk: str | None = None
    created_at: datetime = Field(..., alias="creationDate")
    username: str | None = None
    email: str | None = None
    first_name: str | None = Field(default="", alias="firstName")
    last_name: str | None = Field(default="", alias="lastName")
    organisation: str | None = None

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()

    def to_domain(self) -> UserEntity:
        return UserEntity(
            pk=self.pk,
            created_at=self.created_at,
            username=self.username,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            organisation=self.organisation,
        )


class UserListFilterRequestModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    page: int = Query(1, ge=1)
    per_page: int = Query(10, alias="perPage", validation_alias="perPage")
    full_name: str | None = Query(None, alias="firstName_lastName", validation_alias="firstName_lastName")
    sort_field: UserSortingFieldsEnum | None = Query(None, alias="sortBy", validation_alias="sortBy")

    def to_domain(self) -> UserListFilter:
        full_name = self.full_name.replace(" ", "") if self.full_name else None
        return UserListFilter(
            page=self.page,
            per_page=self.per_page,
            full_name=full_name,
            sort_field=self.sort_field,
        )


class ExpandedUserModel(UserModel):
    organisation: OrganisationModel | None = None
    default_customization_url: str | None = Field(default=None, alias="defaultCustomizationUrl")

    def to_domain(self) -> UserEntity:
        raise NotImplementedError("Read only model is not suitable to build domain entities")


class DeleteUserResponseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    deleted_users: list[str] = Field(default_factory=list, alias="deletedUsers")


class ApproveUserResponseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    approved_users: list[str] = Field(default_factory=list, alias="approvedUsers")


class DeclineUserRequestResponseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    declined_users: list[str] = Field(default_factory=list, alias="declinedUsers")
