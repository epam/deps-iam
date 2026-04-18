import uuid

import pytest
from deps_message_flow.events.common import DomainEvent
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)
from deps_message_flow.messaging.common import Message

from deps_iam.constants import DOCUMENTS_EXCHANGER


@pytest.fixture
def dee():
    return DomainEventEnvelope(
        message=Message(b"test", headers={}),
        aggregate_id="123",
        aggregate_type=DOCUMENTS_EXCHANGER,
        event_id=uuid.uuid4().hex,
        event=DomainEvent(),
    )
