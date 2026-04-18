import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.common import make_message_for_command
from deps_message_flow.commands.consumer import CommandHandlerReplyBuilder
from deps_message_flow.commands.consumer.command_message import CommandMessage
from deps_message_flow.events.mappers import JsonMapper
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_iam.constants import TENANT_COMMANDS_REPLIES
from deps_iam.containers import Application
from deps_iam.domain.dtos import OrganisationListFilter
from deps_iam.domain.events import GetTenantsReply
from deps_iam.domain.interfaces.services import IEmailSender, IOrganisationService

logger = logging.getLogger(__name__)


@inject
def send_invitation_email_handler(
    dee: DomainEventEnvelope,
    email_sender_service: IEmailSender = Provide[Application.services.email_sender],
) -> None:
    try:
        email_sender_service.send_email(
            email=dee.event.user_email,
            inviter=dee.event.inviter_name,
            organisation_pk=dee.event.organisation,
        )
    except Exception as exc:
        logger.error(f"Failed to send invitation email! Reason: {exc}")
    else:
        logger.info(f"An invitation email to '{dee.event.user_email}' successfully sent.")


def test_event_handler(
    dee: DomainEventEnvelope,
) -> None:
    logger.info("Test event")


@inject
def get_tenants_handler(
    command_message: CommandMessage,
    organisation_service: IOrganisationService = Provide[Application.services.organisation],
):
    try:
        organisations = organisation_service.get_organisation_list(OrganisationListFilter())

        command_reply = GetTenantsReply([organisation.pk for organisation in organisations])
        message_reply = make_message_for_command(
            TENANT_COMMANDS_REPLIES,
            JsonMapper().serialize(command_reply),
            command_reply.__class__.__name__,
            "NONE",
        )

        return [CommandHandlerReplyBuilder.with_success(message_reply)]

    except Exception as e:
        command_reply = GetTenantsReply([])
        message_reply = make_message_for_command(
            TENANT_COMMANDS_REPLIES,
            JsonMapper().serialize(command_reply),
            command_reply.__class__.__name__,
            "NONE",
        )

        logger.error(f"Failed to get tenants! \n Reason: {e}")

        return [CommandHandlerReplyBuilder.with_failure(message_reply)]
