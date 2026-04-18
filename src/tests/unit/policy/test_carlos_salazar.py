import pytest

from deps_iam.domain.model import *


@pytest.mark.policy
def test_carlos_salazar_x_list(carlos_salazar_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("X"), Principal("CarlosSalazar"))
    ib_decision = carlos_salazar_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_carlos_salazar_x_read(carlos_salazar_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("X"), Principal("CarlosSalazar"))
    ib_decision = carlos_salazar_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_carlos_salazar_x_write(carlos_salazar_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("X"), Principal("CarlosSalazar"))
    ib_decision = carlos_salazar_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_carlos_salazar_y_list(carlos_salazar_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("Y"), Principal("CarlosSalazar"))
    ib_decision = carlos_salazar_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.ALLOW


@pytest.mark.policy
def test_carlos_salazar_y_read(carlos_salazar_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("Y"), Principal("CarlosSalazar"))
    ib_decision = carlos_salazar_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_carlos_salazar_y_write(carlos_salazar_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("Y"), Principal("CarlosSalazar"))
    ib_decision = carlos_salazar_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.ALLOW


@pytest.mark.policy
def test_carlos_salazar_z_list(carlos_salazar_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("Z"), Principal("CarlosSalazar"))
    ib_decision = carlos_salazar_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.EXPLICIT_DENY


@pytest.mark.policy
def test_carlos_salazar_z_read(carlos_salazar_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("Z"), Principal("CarlosSalazar"))
    ib_decision = carlos_salazar_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.EXPLICIT_DENY


@pytest.mark.policy
def test_carlos_salazar_z_write(carlos_salazar_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("Z"), Principal("CarlosSalazar"))
    ib_decision = carlos_salazar_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.EXPLICIT_DENY
