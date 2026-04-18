from typing import Dict, List, Tuple

from deps_message_flow.events.common import DomainEvent

DomainEventInfo = Tuple[str, str, DomainEvent]


class FakeEventPublisher:
    def __init__(self) -> None:
        self.published_events: List[DomainEventInfo] = []

    def publish(
        self, aggregate_type: str, aggregate_id: str, domain_events: List[DomainEvent], *, headers: Dict[str, str] = {}
    ) -> None:
        for e in domain_events:
            self.published_events.append((aggregate_type, aggregate_id, e))
