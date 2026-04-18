from ..shared import Email
from ..shared.guards import Guard, ImmutableCheck

__all__ = ["PersonalInfo"]


class PersonalInfo:
    first_name = Guard[str](str, ImmutableCheck())
    last_name = Guard[str](str, ImmutableCheck())
    email = Guard[Email](Email, ImmutableCheck())

    def __init__(self, first_name: str, last_name: str, email: Email) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def __str__(self) -> str:
        return f"<PersonalInfo> first_name: {self.first_name}, last_name: {self.last_name}, email: {self.email}"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.first_name == other.first_name
            and self.last_name == other.last_name
            and self.email == other.email
        )
