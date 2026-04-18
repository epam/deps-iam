from itertools import chain
from typing import Sequence

import pytest

from deps_iam.domain.exceptions.policy import PolicyNotFoundError
from deps_iam.domain.model import Policy, Statement


@pytest.fixture
def policy_repo(repositories):
    yield repositories.policy()


@pytest.fixture
def policy(policy_factory):
    return policy_factory()


class TestPolicyRepo:
    def _sort_policies(self, policies_list: list[Policy]) -> None:
        for policy in policies_list:
            policy.statements.sort(
                key=lambda st: (
                    st.effect.value,
                    tuple(a() for a in st.actions),
                    tuple(r() for r in st.resources),
                    tuple(p() for p in st.principals),
                )
            )
        policies_list.sort(key=lambda p: p.id())

    def test_save__successfull(self, policy_repo, resource, policy):
        policy_repo.save(resource(), policy)
        with policy_repo._database.connection() as conn:
            self._check_policy_saved(conn, policy, resource())

    def test_policy_of_id(self, policy_repo, resource, policy):
        policy_repo.save(resource(), policy)
        policy_from_db = policy_repo.policy_of_id(policy.id())
        self._sort_policies([policy, policy_from_db])
        assert policy_from_db == policy
        assert policy_from_db.statements == policy.statements

    def test_policy_of_id__no_policy__raises(self, policy_repo, policy):
        with pytest.raises(PolicyNotFoundError):
            policy_repo.policy_of_id(policy.id())

    def test_delete__policy_exists__successfully_deleted(self, policy_repo, resource, policy):
        policy_repo.save(resource(), policy)
        policy_repo.delete(policy)
        with pytest.raises(PolicyNotFoundError):
            policy_repo.policy_of_id(policy.id())
        with policy_repo._database.connection() as conn:
            self._check_policy_deleted(conn)

    def test_delete_policy__not_exist__not_raises(self, policy_repo, policy):
        policy_repo.delete(policy)
        assert True

    def test_all_policies_of_resource(self, policy_repo, resource, policy_factory):
        policies = policy_factory.build_batch(5)
        for policy in policies:
            policy_repo.save(resource(), policy)
        policies_from_db = policy_repo.all_policies_of_resource(resource())

        for pol in (policies, policies_from_db):
            self._sort_policies(pol)
        assert policies == policies_from_db

    def test_all_policies_of_resource__not_exist__empty_list(self, policy_repo, resource):
        assert policy_repo.all_policies_of_resource(resource()) == []

    def test_all_policies_of_resources(self, policy_repo, resource_factory, policy_factory):
        expected_result = {resource(): policy_factory.build_batch(5) for resource in resource_factory.build_batch(5)}
        for resource_str, policies in expected_result.items():
            self._sort_policies(policies)
            for policy in policies:
                policy_repo.save(resource_str, policy)
        response = policy_repo.all_policies_of_resources(list(expected_result.keys()))
        for policies in response.values():
            self._sort_policies(policies)
        assert response == expected_result

    def test_all_policies_of_resources__partially_not_presented__empty_lists(
        self, policy_repo, resource_factory, policy_factory
    ):
        things_to_save = {resource(): policy_factory.build_batch(5) for resource in resource_factory.build_batch(5)}
        new_resources = {resource(): [] for resource in resource_factory.build_batch(5)}
        for resource_str, policies in things_to_save.items():
            for policy in policies:
                policy_repo.save(resource_str, policy)

        request_resources = list(chain(things_to_save.keys(), new_resources.keys()))
        response = policy_repo.all_policies_of_resources(request_resources)
        for v in (response.values(), things_to_save.values()):
            for vv in v:
                self._sort_policies(vv)
        assert response == things_to_save

    def test_all_policies_of_resources__no_policy_exist__dict_with_empty_lists(self, policy_repo, resource_factory):
        assert policy_repo.all_policies_of_resources([r() for r in resource_factory.build_batch(5)]) == {}

    def _check_policy_saved(self, conn, policy, resource):
        pid = policy.id()
        assert list(conn.execute("SELECT id FROM policy;").fetchall()) == [(pid,)]
        assert list(conn.execute("SELECT policy_id FROM statement;").fetchall()) == [
            (pid,) for _ in range(len(policy.statements))
        ]
        assert list(conn.execute("SELECT policy_id, resource FROM resource_has_policy;").fetchall()) == [
            (pid, resource)
        ]

    def _check_policy_deleted(self, conn):
        assert list(conn.execute("SELECT id FROM policy;").fetchall()) == []
        assert list(conn.execute("SELECT policy_id FROM statement;").fetchall()) == []
        assert list(conn.execute("SELECT policy_id, resource FROM resource_has_policy;").fetchall()) == []
