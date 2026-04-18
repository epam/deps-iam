from threading import Timer

import pytest

POLLING_PERIOD = 0.01


@pytest.fixture
def to_event_publisher(application, messaging):
    to_producer = messaging.transactional_outbox_producer()

    with messaging.true_producer.override(to_producer):
        application.reset_singletons()
        yield application.domain_event_publisher()
