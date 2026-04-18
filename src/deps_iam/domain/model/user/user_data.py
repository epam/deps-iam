from typing import Optional, TypedDict

__all__ = ["UserData"]


class UserData(TypedDict):
    first_name: str
    last_name: str
    email: str
    organisation: Optional[str]
