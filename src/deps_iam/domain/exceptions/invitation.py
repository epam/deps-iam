from .base import IAMException


class IncorrectEmailException(IAMException):
    code = "incorrect_email_format"

    def __init__(self, email: str) -> None:
        self.email = email
        self.msg = f"Incorrect email: {self.email}"
        super().__init__(self.msg)
