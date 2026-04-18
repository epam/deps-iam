import pytest
from deps_message_flow.sagas.orchestration import SerializedSagaData

from deps_iam.domain.exceptions import NotFoundError


def test_saga_repository__find__failure(saga_instance_repo, saga_instance):
    with pytest.raises(NotFoundError):
        saga_instance_repo.find("qwerty")


def test_saga_repository__save__update__find__success(saga_instance_repo, saga_instance):
    saved_saga_instance = saga_instance_repo.save(saga_instance)

    saved_saga_instance.saga_type = "NewSagaType"
    saved_saga_instance.state_name = "NewState"
    saved_saga_instance.last_request_id = "NewLastRequestId"
    saved_saga_instance.serialized_saga_data = SerializedSagaData(
        saga_data_type="NewData",
        saga_data_json="{'new': true}",
    )
    saved_saga_instance.end_state = True
    saved_saga_instance.compensating = True
    saved_saga_instance.failed = True

    updated_saga_instance = saga_instance_repo.update(saved_saga_instance)

    found_saga_instance = saga_instance_repo.find(updated_saga_instance.saga_id)

    assert saved_saga_instance.saga_type == found_saga_instance.saga_type
    assert saved_saga_instance.state_name == found_saga_instance.state_name
    assert saved_saga_instance.last_request_id == found_saga_instance.last_request_id
    assert saved_saga_instance.serialized_saga_data == found_saga_instance.serialized_saga_data
    assert saved_saga_instance.end_state == found_saga_instance.end_state
    assert saved_saga_instance.compensating == found_saga_instance.compensating
    assert saved_saga_instance.failed == found_saga_instance.failed
