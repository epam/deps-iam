from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CommonUserEntity:
    pk: Optional[str]
    created_at: datetime
    first_name: str
    last_name: str
    username: Optional[str] = None
    email: Optional[str] = None


@dataclass
class UserEntity(CommonUserEntity):
    organisation: Optional[str] = None
