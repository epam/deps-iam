import smtplib
from email.parser import Parser
from unittest import mock

import pytest
from jinja2 import Template

from deps_iam import constants


@pytest.fixture
def email_sender(services):
    email_sender = services.email_sender
    email_sender.reset_override()
    yield email_sender()


class TestEmailSender:
    def test_send_mail__email_sent(self, email_sender, monkeypatch):
        smtp_mock = mock.Mock(smtplib.SMTP)
        msg_body = "Test email"
        monkeypatch.setattr(email_sender, "_build_message", mock.Mock(return_value=msg_body))
        email = "test@gmail.com"
        with mock.patch("smtplib.SMTP", return_value=smtp_mock):
            email_sender.send_email(email, "inviter@epam.com", "best-org")

        smtp_mock.starttls.assert_called_once()
        smtp_mock.login.assert_called_once_with(email_sender._login, email_sender._password)
        smtp_mock.sendmail.assert_called_with(email_sender._from_addr, [email], msg_body)

    def test_generate_invitation_link__correct_link_generated(self, email_sender, config):
        org = "testing"
        expected = f"{config.external_url()}/join/{org}"
        generated = email_sender._generate_invitation_link(org)
        assert generated == expected

    def test_build_message__correct_message_created(self, email_sender, monkeypatch):
        msg_body = "Test email"
        monkeypatch.setattr(email_sender, "_get_email_body", mock.Mock(return_value=msg_body))
        receiver = "test@mail.ru"
        email_message = email_sender._build_message(receiver, "inviter@mail.ru", "cool-org")

        assert receiver in email_message
        assert constants.EMAIL_INVITATION_SUBJECT in email_message
        assert email_sender._login in email_message
        assert email_sender._from_addr in email_message

    def test_get_email_body__formatted_string_returned(
        self, email_sender, config, monkeypatch, mocker, organisation_factory, organisation_repository_mock
    ):
        inviter = "inviter@mail.ru"
        org = organisation_factory()
        organisation_repository_mock.get.return_value = org
        link = f"{config.external_url()}/join/{org.pk}"
        tmplt_data = Template("{{inviter}},{{organisation}},{{invitation_link}},{{support_email}}")
        monkeypatch.setattr(email_sender._jinja_env, "get_template", mocker.Mock(return_value=tmplt_data))

        email_body = email_sender._get_email_body(inviter, org.pk)

        expected = tmplt_data.render(
            inviter=inviter,
            organisation=org.name,
            invitation_link=link,
            support_email=email_sender._from_addr,
        )
        assert email_body == expected

    @pytest.mark.current_test
    def test_send_email__event_type_header_added(self, email_sender, monkeypatch):
        email = "test@gmail.com"
        inviter = "inviter@epam.com"
        organisation_pk = "best-org"

        smtp_mock = mock.MagicMock()
        monkeypatch.setattr(smtplib, "SMTP", mock.Mock(return_value=smtp_mock))

        email_sender.send_email(email, inviter, organisation_pk)

        message_str = email_sender._build_message(email, inviter, organisation_pk)

        message = Parser().parsestr(message_str)

        assert message[constants.EMAIL_EVENT_TYPE_HEADER] == email_sender._event_type
