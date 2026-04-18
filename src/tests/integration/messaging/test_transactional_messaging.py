from contextlib import suppress

import pytest
from deps_message_flow.events.publisher import DomainEventPublisher

from deps_iam.domain.entities import Organisation
from tests.fakes import AGGREGATE, QUEUE, FakeEvent


@pytest.fixture
def message_repo(messaging):
    yield messaging.message_repo()


@pytest.fixture
def organisation_repo(organisation_repository):
    yield organisation_repository


@pytest.fixture
def event():
    return FakeEvent(
        message="org1",
    )


@pytest.fixture
def organisation():
    return Organisation(
        name="org1",
    )


def publish_event(event_publisher: DomainEventPublisher, event) -> None:
    event_publisher.publish(
        AGGREGATE,
        QUEUE,
        [event],
    )


def organisation_added(organisation_repo) -> bool:
    return len(organisation_repo.get_list()) == 1


def message_produced(message_repo) -> bool:
    return len(list(message_repo.get_all())) == 1


def test_committed_state_and_event__both_saved_and_produced(
    uow,
    organisation_repo,
    to_event_publisher,
    event,
    organisation,
    message_repo,
):
    with uow:
        organisation_repo.create(organisation)
        publish_event(to_event_publisher, event)
        uow.commit()

    assert organisation_added(organisation_repo) and message_produced(message_repo)


def test_not_commited_state_and_event__nothing(
    uow,
    organisation_repo,
    to_event_publisher,
    event,
    organisation,
    message_repo,
):
    with uow:
        organisation_repo.create(organisation)
        publish_event(to_event_publisher, event)

    assert not organisation_added(organisation_repo) and not message_produced(message_repo)


def test_successfull_event_failed_state__nothing(
    uow,
    organisation_repo,
    to_event_publisher,
    event,
    organisation,
    message_repo,
):
    with suppress(RuntimeError):
        with uow:
            publish_event(to_event_publisher, event)
            raise RuntimeError
            organisation_repo.create(organisation)
            uow.commit()

    assert not organisation_added(organisation_repo) and not message_produced(message_repo)


def test_successfull_state_failed_event__nothing(
    uow,
    organisation_repo,
    to_event_publisher,
    event,
    organisation,
    message_repo,
):
    with suppress(RuntimeError):
        with uow:
            organisation_repo.create(organisation)
            raise RuntimeError
            publish_event(to_event_publisher, event)
            uow.commit()

    assert not organisation_added(organisation_repo) and not message_produced(message_repo)
