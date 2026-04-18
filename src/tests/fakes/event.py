from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent


@dataclass
class FakeEvent(DomainEvent):
    message: str
