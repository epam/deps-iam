import pytest

from deps_iam.domain.model import *


@pytest.mark.policy
def test_mary_major_x_list(mary_major_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("X"), Principal("MaryMajor"))
    ib_decision = mary_major_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.ALLOW


@pytest.mark.policy
def test_mary_major_x_read(mary_major_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("X"), Principal("MaryMajor"))
    ib_decision = mary_major_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.ALLOW


@pytest.mark.policy
def test_mary_major_x_write(mary_major_ibp: Policy, x_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("X"), Principal("MaryMajor"))
    ib_decision = mary_major_ibp.evaluate(request_context)
    rb_decision = x_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_mary_major_y_list(mary_major_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("Y"), Principal("MaryMajor"))
    ib_decision = mary_major_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_mary_major_y_read(mary_major_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("Y"), Principal("MaryMajor"))
    ib_decision = mary_major_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_mary_major_y_write(mary_major_ibp: Policy, y_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("Y"), Principal("MaryMajor"))
    ib_decision = mary_major_ibp.evaluate(request_context)
    rb_decision = y_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_mary_major_z_list(mary_major_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("List"), Resource("Y"), Principal("MaryMajor"))
    ib_decision = mary_major_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_mary_major_z_read(mary_major_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Read"), Resource("Y"), Principal("MaryMajor"))
    ib_decision = mary_major_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.IMPLICIT_DENY


@pytest.mark.policy
def test_mary_major_z_write(mary_major_ibp: Policy, z_resource_based_policy: Policy):
    request_context = RequestStatement(Action("Write"), Resource("Y"), Principal("MaryMajor"))
    ib_decision = mary_major_ibp.evaluate(request_context)
    rb_decision = z_resource_based_policy.evaluate(request_context)

    assert ib_decision == PolicyDecision.ALLOW
    assert rb_decision == PolicyDecision.IMPLICIT_DENY
