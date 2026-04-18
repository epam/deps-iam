from ....shared.guards import Guard, ImmutableCheck

__all__ = ["Principal"]


class Principal:
    value = Guard[str](str, ImmutableCheck())

    def __init__(self, value: str) -> None:
        self.value = value

    def __call__(self) -> str:
        return self.value

    def __str__(self) -> str:
        return f"<Principal>: {self.value}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.value == other.value
