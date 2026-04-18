import pytest

from deps_iam.domain.model import *


@pytest.mark.policy
def test_john_smith_x_list(john_smith_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("X"), Principal("JohnSmith"))
    ib_decision = john_smith_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.ALLOW


@pytest.mark.policy
def test_john_smith_x_read(john_smith_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("X"), Principal("JohnSmith"))
    ib_decision = john_smith_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.ALLOW


@pytest.mark.policy
def test_john_smith_x_write(john_smith_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("X"), Principal("JohnSmith"))
    ib_decision = john_smith_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_john_smith_y_list(john_smith_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("Y"), Principal("JohnSmith"))
    ib_decision = john_smith_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_john_smith_y_read(john_smith_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("Y"), Principal("JohnSmith"))
    ib_decision = john_smith_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_john_smith_y_write(john_smith_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("Y"), Principal("JohnSmith"))
    ib_decision = john_smith_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_john_smith_z_list(john_smith_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("Y"), Principal("JohnSmith"))
    ib_decision = john_smith_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_john_smith_z_read(john_smith_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("Y"), Principal("JohnSmith"))
    ib_decision = john_smith_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_john_smith_z_write(john_smith_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("Y"), Principal("JohnSmith"))
    ib_decision = john_smith_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.IMPLICIT_DENY
    assert rb_decision == PolicyDecision.IMPLICIT_DENY
