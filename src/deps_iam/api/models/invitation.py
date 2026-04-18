import re

from pydantic import BaseModel, ConfigDict, field_validator

from deps_iam.domain.entities import Invitation
from deps_iam.domain.exceptions import IncorrectEmailException

emails_regexp = re.compile(
    r"(?:[A-Za-z0-9!$&*?^_{}~-]+(?:\.[A-Za-z0-9!$&*?^_{}~-]+)*|\"(?:[\x01-"  # noqa: P103
    + r"\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:"
    + r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?|\[(?:(?:"
    + r"(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9]"
    + r"[0-9]|[1-9]?[0-9])|[A-Za-z0-9-]*[A-Za-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-"
    + r"\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
)


class InvitationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str

    def to_domain(self) -> Invitation:
        return Invitation(**self.model_dump())

    @field_validator("email")
    @classmethod
    def validate_email(cls, email: str) -> str:
        if emails_regexp.fullmatch(email):
            return email.lower()
        raise IncorrectEmailException(email)
