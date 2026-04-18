import pytest

from deps_iam.domain.model import Action, ActionMatchSpecification


@pytest.mark.action
def test_match():
    action_specification = ActionMatchSpecification(Action("s3:PutObject"))
    action = Action("s3:PutObject")

    assert action_specification.is_satisfied_by(action)


@pytest.mark.action
def test_match_wildcard_right():
    action_specification = ActionMatchSpecification(Action("s3:Put*"))
    action = Action("s3:PutObject")

    assert action_specification.is_satisfied_by(action)


@pytest.mark.action
def test_match_wildcard_left():
    action_specification = ActionMatchSpecification(Action("s3:*Object"))
    action = Action("s3:PutObject")

    assert action_specification.is_satisfied_by(action)


@pytest.mark.action
def test_match_wildcard_both():
    action_specification = ActionMatchSpecification(Action("s3:*tObje*"))
    action = Action("s3:PutObject")

    assert action_specification.is_satisfied_by(action)
