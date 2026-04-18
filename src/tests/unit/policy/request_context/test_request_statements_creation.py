import pytest

from deps_iam.domain.model import *


@pytest.mark.policy
def test_request_statements_creation():
    request_context = RequestContext(
        Action("AddLabel"),
        [
            Resource("drn:document:<tenant-id>:/<group-id>/label/{resource_id}"),
            Resource("drn:document:<tenant-id>:/<group-id>/document/{resource_id}"),
        ],
        Principal("CarlosSalazar"),
        {
            "drn:document:<tenant-id>:/<group-id>/label/{resource_id}": [1],
            "drn:document:<tenant-id>:/<group-id>/document/{resource_id}": [1, 2, 3],
        },
    )
    request_statements = [
        RequestStatement(
            Action("AddLabel"),
            Resource("drn:document:<tenant-id>:/<group-id>/label/1"),
            Principal("CarlosSalazar"),
        ),
        RequestStatement(
            Action("AddLabel"),
            Resource("drn:document:<tenant-id>:/<group-id>/document/1"),
            Principal("CarlosSalazar"),
        ),
        RequestStatement(
            Action("AddLabel"),
            Resource("drn:document:<tenant-id>:/<group-id>/document/2"),
            Principal("CarlosSalazar"),
        ),
        RequestStatement(
            Action("AddLabel"),
            Resource("drn:document:<tenant-id>:/<group-id>/document/3"),
            Principal("CarlosSalazar"),
        ),
    ]

    assert request_statements == request_context.request_statements


@pytest.mark.policy
def test_request_statements_creation_empty_resource_data():
    request_context = RequestContext(
        Action("CreateLabel"),
        [
            Resource("drn:document:<tenant-id>:/<group-id>/label/"),
        ],
        Principal("CarlosSalazar"),
        {},
    )
    request_statements = [
        RequestStatement(
            Action("CreateLabel"),
            Resource("drn:document:<tenant-id>:/<group-id>/label/"),
            Principal("CarlosSalazar"),
        )
    ]

    assert request_statements == request_context.request_statements
