import pytest

from deps_iam.domain.model import *


@pytest.mark.policy
def test_zhang_wei_x_list(zhang_wei_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("X"), Principal("ZhangWei"))
    ib_decision = zhang_wei_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_zhang_wei_x_read(zhang_wei_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("X"), Principal("ZhangWei"))
    ib_decision = zhang_wei_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_zhang_wei_x_write(zhang_wei_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("X"), Principal("ZhangWei"))
    ib_decision = zhang_wei_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_zhang_wei_y_list(zhang_wei_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("Y"), Principal("ZhangWei"))
    ib_decision = zhang_wei_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.ALLOW


@pytest.mark.policy
def test_zhang_wei_y_read(zhang_wei_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("Y"), Principal("ZhangWei"))
    ib_decision = zhang_wei_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.ALLOW


@pytest.mark.policy
def test_zhang_wei_y_write(zhang_wei_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("Y"), Principal("ZhangWei"))
    ib_decision = zhang_wei_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_zhang_wei_z_list(zhang_wei_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("Z"), Principal("ZhangWei"))
    ib_decision = zhang_wei_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.ALLOW


@pytest.mark.policy
def test_zhang_wei_z_read(zhang_wei_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("Z"), Principal("ZhangWei"))
    ib_decision = zhang_wei_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.ALLOW


@pytest.mark.policy
def test_zhang_wei_z_write(zhang_wei_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("Z"), Principal("ZhangWei"))
    ib_decision = zhang_wei_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.ALLOW
