import pytest

from deps_iam.domain.model import *

USER_SUBJECT = "user_subject"


@pytest.fixture
def john_smith_ibp():
    return Policy(
        id_=EntityId(),
        statements=[
            Statement(
                Effect.ALLOW,
                [Action("List"), Action("Read")],
                [Resource("X")],
            ),
        ],
    )


@pytest.fixture
def carlos_salazar_ibp():
    return Policy(
        id_=EntityId(),
        statements=[
            Statement(
                Effect.ALLOW,
                [Action("List"), Action("Read")],
                [Resource("Y"), Resource("Z")],
            ),
        ],
    )


@pytest.fixture
def mary_major_ibp():
    return Policy(
        id_=EntityId(),
        statements=[
            Statement(
                Effect.ALLOW,
                [Action("List"), Action("Read"), Action("Write")],
                [Resource("X"), Resource("Y"), Resource("Z")],
            ),
        ],
    )


@pytest.fixture
def zhang_wei_ibp():
    return Policy(
        id_=EntityId(),
        statements=[],
    )


@pytest.fixture
def x_resource_based_policy():
    return Policy(
        id_=EntityId(),
        statements=[
            Statement(
                Effect.ALLOW,
                [Action("List"), Action("Read")],
                [Resource("X")],
                [Principal("JohnSmith"), Principal("MaryMajor")],
            ),
        ],
    )


@pytest.fixture
def y_resource_based_policy():
    return Policy(
        id_=EntityId(),
        statements=[
            Statement(
                Effect.ALLOW,
                [Action("List"), Action("Write")],
                [Resource("Y")],
                [Principal("CarlosSalazar")],
            ),
            Statement(
                Effect.ALLOW,
                [Action("List"), Action("Read")],
                [Resource("Y")],
                [Principal("ZhangWei")],
            ),
        ],
    )


@pytest.fixture
def z_resource_based_policy():
    return Policy(
        id_=EntityId(),
        statements=[
            Statement(
                Effect.DENY,
                [Action("*")],
                [Resource("Z")],
                [Principal("CarlosSalazar")],
            ),
            Statement(
                Effect.ALLOW,
                [Action("*")],
                [Resource("Z")],
                [Principal("ZhangWei")],
            ),
        ],
    )


@pytest.fixture
def valentin_vorobyev_ibp():
    return Policy(
        id_=EntityId(),
        statements=[
            Statement(
                Effect.ALLOW,
                [Action("AddLabel"), Action("CreateLabel")],
                [Resource("drn:document:<tenant-id>:/<group-id>/*")],
            ),
        ],
    )


@pytest.fixture
def document1_resource_based_policy():
    return Policy(
        id_=EntityId(),
        statements=[
            Statement(
                Effect.DENY,
                [Action("*")],
                [Resource("drn:document:<tenant-id>:/<group-id>/document/1")],
                [Principal("ValentinVorobyev")],
            ),
        ],
    )


@pytest.fixture
def this_user_tenant_read_only_ibp(this_user):
    return Policy(
        EntityId(),
        statements=[
            Statement(
                Effect.ALLOW,
                [Action("document:Get*"), Action("document:List*")],
                [Resource(f"drn:document:{this_user['organisation']}:/admins/*")],
            ),
        ],
    )


@pytest.fixture
def request_parser(application):
    yield application.infrastructure_services.request_parsing()
