from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from deps_iam.domain.dtos import DateTimeRange, UserListFilter, UserUpdateObject
from deps_iam.domain.entities.user import UserEntity


class DateTimeRangeModel(BaseModel):
    start: datetime | None = None
    end: datetime | None = None


class UserListFilterModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pks: list[str] | None = None
    created_at: DateTimeRangeModel | None = Field(None, alias="createdAt")
    username: str | None = None
    email: str | None = None
    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")

    def to_domain(self) -> UserListFilter:
        return UserListFilter(
            pks=self.pks,
            created_at=self.created_at and DateTimeRange(self.created_at.start, self.created_at.end),
            username=self.username,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
        )


class UserUpdateObjectModel(BaseModel):
    """
    Only contains parameters allowed to modify
    """

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    first_name: str | None = Field(None, alias="firstName")
    last_name: str | None = Field(None, alias="lastName")

    def to_domain(self) -> UserUpdateObject:
        return UserUpdateObject(
            first_name=self.first_name,
            last_name=self.last_name,
        )

    @model_validator(mode="before")
    @classmethod
    def validate_at_least_one_field_exists(cls, function_arguments_dict: Any) -> Any:
        if isinstance(function_arguments_dict, dict) and not any(function_arguments_dict.values()):
            raise ValueError("No arguments given")
        return function_arguments_dict


class UserCreateModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    email: str
    username: str | None = None
    first_name: str | None = Field(default="", alias="firstName")
    last_name: str | None = Field(default="", alias="lastName")
    organisation: str | None = None

    def to_domain(self) -> UserEntity:
        return UserEntity(
            pk=str(uuid4()),
            created_at=datetime.utcnow(),
            username=self.username,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            organisation=self.organisation,
        )
