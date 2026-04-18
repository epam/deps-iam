from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .pagination import PaginationObject


class InvitationSortingFieldEnum(Enum):
    email_desc = "email.desc"
    email_asc = "email.asc"


@dataclass
class InvitationListFilter(PaginationObject):
    user_pk: Optional[str] = None
    sorting_field: Optional[InvitationSortingFieldEnum] = None
    search_term: Optional[str] = None
