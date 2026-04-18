import pytest

from deps_iam.domain.events import SendInvitationEmailEvent
from deps_iam.events_handler.handlers import send_invitation_email_handler


@pytest.fixture
def email_sender_mock(mocker, services):
    mock = mocker.Mock(services.email_sender())
    with services.email_sender.override(mock):
        yield mock


def test_send_invitation_email_handler__email_sender_invoked(dee, email_sender_mock):
    dee._event = SendInvitationEmailEvent(
        user_email="test@test.com",
        inviter_name="John",
        organisation="org",
    )

    send_invitation_email_handler(dee)

    email_sender_mock.send_email.assert_called_with(
        email="test@test.com",
        inviter="John",
        organisation_pk="org",
    )
