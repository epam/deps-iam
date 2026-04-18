import pytest

from deps_iam.domain.model import *
from tests.fakes import *


@pytest.mark.policy
def test_carlos_salazar_x_list(carlos_salazar_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestContext(Action("List"), [Resource("X")], Principal("CarlosSalazar"), {})

    policies = {
        "CarlosSalazar": [carlos_salazar_ibp],
        "X": [x_resource_based_policy],
    }
    pds = PermissionDeterminingService(policies, request_context)

    assert not pds.has_permission


@pytest.mark.policy
def test_carlos_salazar_x_read(carlos_salazar_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestContext(Action("Read"), [Resource("X")], Principal("CarlosSalazar"), {})
    policies = {
        "CarlosSalazar": [carlos_salazar_ibp],
        "X": [x_resource_based_policy],
    }
    pds = PermissionDeterminingService(policies, request_context)

    assert not pds.has_permission


@pytest.mark.policy
def test_carlos_salazar_x_write(carlos_salazar_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestContext(Action("Write"), [Resource("X")], Principal("CarlosSalazar"), {})
    policies = {
        "CarlosSalazar": [carlos_salazar_ibp],
        "X": [x_resource_based_policy],
    }
    pds = PermissionDeterminingService(policies, request_context)

    assert not pds.has_permission


@pytest.mark.policy
def test_carlos_salazar_y_list(carlos_salazar_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestContext(Action("List"), [Resource("Y")], Principal("CarlosSalazar"), {})
    policies = {
        "CarlosSalazar": [carlos_salazar_ibp],
        "Y": [y_resource_based_policy],
    }
    pds = PermissionDeterminingService(policies, request_context)

    assert pds.has_permission


@pytest.mark.policy
def test_carlos_salazar_y_read(carlos_salazar_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestContext(Action("Read"), [Resource("Y")], Principal("CarlosSalazar"), {})
    policies = {
        "CarlosSalazar": [carlos_salazar_ibp],
        "Y": [y_resource_based_policy],
    }
    pds = PermissionDeterminingService(policies, request_context)

    assert pds.has_permission


@pytest.mark.policy
def test_carlos_salazar_y_write(carlos_salazar_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestContext(Action("Write"), [Resource("Y")], Principal("CarlosSalazar"), {})
    policies = {
        "CarlosSalazar": [carlos_salazar_ibp],
        "Y": [y_resource_based_policy],
    }
    pds = PermissionDeterminingService(policies, request_context)

    assert pds.has_permission


@pytest.mark.policy
def test_carlos_salazar_z_list(carlos_salazar_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestContext(Action("List"), [Resource("Z")], Principal("CarlosSalazar"), {})
    policies = {
        "CarlosSalazar": [carlos_salazar_ibp],
        "Z": [z_resource_based_policy],
    }
    pds = PermissionDeterminingService(policies, request_context)

    assert not pds.has_permission


@pytest.mark.policy
def test_carlos_salazar_z_read(carlos_salazar_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestContext(Action("Read"), [Resource("Z")], Principal("CarlosSalazar"), {})
    policies = {
        "CarlosSalazar": [carlos_salazar_ibp],
        "Z": [z_resource_based_policy],
    }
    pds = PermissionDeterminingService(policies, request_context)

    assert not pds.has_permission


@pytest.mark.policy
def test_carlos_salazar_z_write(carlos_salazar_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestContext(Action("Write"), [Resource("Z")], Principal("CarlosSalazar"), {})
    policies = {
        "CarlosSalazar": [carlos_salazar_ibp],
        "Z": [z_resource_based_policy],
    }
    pds = PermissionDeterminingService(policies, request_context)

    assert not pds.has_permission
