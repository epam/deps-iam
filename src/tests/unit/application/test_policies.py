import pytest

from deps_iam.application import PolicyService
from deps_iam.domain.model import Group, User
from tests.fakes import FakePolicyRepository


@pytest.mark.sign_up_policy_storing
def test_save_group_policies__successful(
    policy_service: PolicyService,
    domain_group: Group,
    fake_policy_repository: FakePolicyRepository,
):
    policy_service.save_group_policies(domain_group)

    assert len(fake_policy_repository.all_policies_of_resource(domain_group.drn)) == 1
    for role in domain_group.roles.values():
        assert len(fake_policy_repository.all_policies_of_resource(role.drn)) == 1


@pytest.mark.sign_up_policy_storing
def test_save_user_policies__successful(
    policy_service: PolicyService,
    domain_group: Group,
    fake_policy_repository: FakePolicyRepository,
    domain_user: User,
):
    policy_service.save_group_policies(domain_group)
    domain_group.accept(domain_user.id)
    domain_user.join_group(domain_group)

    policy_service.save_user_policies(domain_user)

    assert len(fake_policy_repository.all_policies_of_resource(domain_user.drn)) == 2


def test_delete_policies(policy_service, fake_policy_repository, domain_group, domain_user):
    policy_service.save_group_policies(domain_group)
    domain_group.accept(domain_user.id)
    domain_user.join_group(domain_group)

    drns = [domain_group.drn, *[val.drn for val in domain_group.roles.values()]]

    assert fake_policy_repository._policy_db
    policy_service.delete_policies(drns)
    assert not fake_policy_repository._policy_db
