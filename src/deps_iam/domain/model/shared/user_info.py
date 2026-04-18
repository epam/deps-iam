from ..shared import Email, EntityId
from ..shared.guards import Guard, ImmutableCheck

__all__ = ["UserInfo"]


class UserInfo:
    id = Guard[EntityId](EntityId, ImmutableCheck())
    first_name = Guard[str](str, ImmutableCheck())
    last_name = Guard[str](str, ImmutableCheck())
    email = Guard[Email](Email, ImmutableCheck())

    def __init__(self, id_: EntityId, first_name: str, last_name: str, email: Email) -> None:
        self.id = id_
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def __str__(self) -> str:
        return (
            f"<UserInfo> id: {self.id}, first_name: {self.first_name}, "
            + f"last_name: {self.last_name}, email: {self.email}"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)  # noqa: WPS222
            and self.id == other.id
            and self.first_name == other.first_name
            and self.last_name == other.last_name
            and self.email == other.email
        )
