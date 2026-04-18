from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Union

from .pagination import PaginationObject


class OrganisationTypesEnum(Enum):
    PERSONAL = auto()
    NON_PERSONAL = auto()


@dataclass
class OrganisationListFilter(PaginationObject):
    user_pk: Optional[str] = None
    organisation_type: Optional[OrganisationTypesEnum] = None


EMPTY = object


@dataclass
class OrganisationUpdate:
    name: Union[Optional[str], EMPTY] = EMPTY
    customization_url: Union[Optional[str], EMPTY] = EMPTY
