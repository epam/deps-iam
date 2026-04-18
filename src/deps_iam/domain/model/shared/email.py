from ..shared.guards import FormatCheck, Guard, ImmutableCheck

__all__ = ["Email"]

EMAIL_FORMAT = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"


class Email:
    value = Guard[str](str, ImmutableCheck(), FormatCheck(EMAIL_FORMAT))

    def __init__(self, value: str) -> None:
        self.value = value

    def __call__(self) -> str:
        return self.value

    def __str__(self) -> str:
        return f"<Email>: {self.value}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.value == other.value
