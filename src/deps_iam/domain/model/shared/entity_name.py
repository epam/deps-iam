from ..shared.guards import Guard, ImmutableCheck

__all__ = ["EntityName"]


class EntityName:
    name = Guard[str](str, ImmutableCheck())
    drn = Guard[str](str, ImmutableCheck())

    def __init__(self, name: str, drn: str) -> None:
        self.name = name
        self.drn = drn

    def __str__(self) -> str:
        return f"<EntityName> name: {self.name}, drn: {self.drn}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.name == other.name and self.drn == other.drn  # noqa: WPS221
