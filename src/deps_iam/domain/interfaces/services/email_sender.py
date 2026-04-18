from abc import ABC, abstractmethod


class IEmailSender(ABC):
    @abstractmethod
    def send_email(self, email: str, inviter: str, organisation_pk: str) -> None:
        pass
