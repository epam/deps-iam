from dataclasses import dataclass
from enum import Enum
from typing import Generic, Optional, TypeVar

from deps_iam.domain.entities import CommonUserEntity, Organisation, UserEntity

from .datetime_range import DateTimeRange
from .pagination import PaginationObject


@dataclass
class UserUpdateObject:
    """
    Only contains parameters allowed to modify
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organisation: Optional[str] = None

    @classmethod
    def from_entity(cls, entity: UserEntity) -> "UserUpdateObject":
        return cls(
            first_name=entity.first_name,
            last_name=entity.last_name,
            organisation=entity.organisation,
        )


@dataclass
class ExpandedUser(CommonUserEntity):
    organisation: Optional[Organisation] = None
    default_customization_url: Optional[str] = None


class UserSortingFieldsEnum(Enum):
    full_name_asc = "firstName_lastName.asc"
    full_name_desc = "firstName_lastName.desc"


@dataclass
class UserListFilter(PaginationObject):
    pks: Optional[list[str]] = None
    created_at: Optional[DateTimeRange] = None
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    sort_field: Optional[UserSortingFieldsEnum] = None
    emails: Optional[list[str]] = None


@dataclass
class ListMetaDataObject:
    total: int
    size: int


T = TypeVar("T")


@dataclass
class ListDataObject(Generic[T]):
    meta: ListMetaDataObject
    result: list[T]  # noqa: WPS110
