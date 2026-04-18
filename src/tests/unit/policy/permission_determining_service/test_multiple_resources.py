import pytest

from deps_iam.domain.model import *


@pytest.mark.policy
def test_multiple_resources_ibp_only(valentin_vorobyev_ibp: Policy):
    request_context = RequestContext(
        Action("AddLabel"),
        [
            Resource("drn:document:<tenant-id>:/<group-id>/label/{resource_id}"),
            Resource("drn:document:<tenant-id>:/<group-id>/document/{resource_id}"),
        ],
        Principal("ValentinVorobyev"),
        {
            "drn:document:<tenant-id>:/<group-id>/label/{resource_id}": [1],
            "drn:document:<tenant-id>:/<group-id>/document/{resource_id}": [1, 2, 3],
        },
    )
    policies = {"ValentinVorobyev": [valentin_vorobyev_ibp]}
    pds = PermissionDeterminingService(policies, request_context)

    assert pds.has_permission
    assert [] == pds.denied_resources


@pytest.mark.policy
def test_multiple_resources_rbp_deny(
    valentin_vorobyev_ibp: Policy,
    document1_resource_based_policy: Policy,
):
    request_context = RequestContext(
        Action("AddLabel"),
        [
            Resource("drn:document:<tenant-id>:/<group-id>/label/{resource_id}"),
            Resource("drn:document:<tenant-id>:/<group-id>/document/{resource_id}"),
        ],
        Principal("ValentinVorobyev"),
        {
            "drn:document:<tenant-id>:/<group-id>/label/{resource_id}": [1],
            "drn:document:<tenant-id>:/<group-id>/document/{resource_id}": [1, 2, 3],
        },
    )
    policies = {
        "ValentinVorobyev": [valentin_vorobyev_ibp],
        "drn:document:<tenant-id>:/<group-id>/document/1": [document1_resource_based_policy],
    }
    pds = PermissionDeterminingService(
        policies,
        request_context,
    )

    assert not pds.has_permission
    assert "drn:document:<tenant-id>:/<group-id>/document/1" in pds.denied_resources
