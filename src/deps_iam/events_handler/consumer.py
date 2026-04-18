import logging

from deps_message_flow.commands.consumer import (
    CommandDispatcher,
    CommandHandlersBuilder,
)
from deps_message_flow.events.subscriber import (
    DomainEventDispatcher,
    DomainEventHandlersBuilder,
)
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer

from deps_iam.constants import (
    COMMANDS_QUEUE,
    DOCUMENTS_EXCHANGER,
    QUEUE,
    TENANT_COMMANDS,
)
from deps_iam.domain.events import GetTenants, SendInvitationEmailEvent, TestEvent

_logger = logging.getLogger(__name__)


def make_consumer(subscriber: IMessageConsumer, producer: IMessageProducer) -> IMessageConsumer:
    from deps_iam.events_handler.handlers import (  # noqa: WPS433
        get_tenants_handler,
        send_invitation_email_handler,
        test_event_handler,
    )

    events_handlers = (
        DomainEventHandlersBuilder.for_aggregate_type(DOCUMENTS_EXCHANGER)
        .on_event(TestEvent, test_event_handler)
        .on_event(SendInvitationEmailEvent, send_invitation_email_handler)
        .for_queue(QUEUE)
        .build()
    )

    commands_handlers = (
        CommandHandlersBuilder.from_channel(TENANT_COMMANDS)
        .on_message(GetTenants, get_tenants_handler)
        .for_queue(COMMANDS_QUEUE)
        .build()
    )

    ded = DomainEventDispatcher(events_handlers, subscriber)
    ded.initialize()

    cd = CommandDispatcher(commands_handlers, subscriber, producer)
    cd.initialize()

    _logger.info("Start consuming...")

    return subscriber
