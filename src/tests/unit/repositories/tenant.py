import pytest

from deps_iam.domain.exceptions import TenantNotFoundError


def test_tenant_of_id__tenant_exists__return_tenant(fake_tenant_repository, tenant_factory):
    fake_tenant_repository._db[tenant_factory.id.value] = tenant_factory
    res = fake_tenant_repository.tenant_of_id(tenant_factory.id.value)
    assert res == tenant_factory


def test_tenant_of_id__tenant_does_not_exist__raise_error(fake_tenant_repository, tenant_factory):
    with pytest.raises(TenantNotFoundError):
        fake_tenant_repository.tenant_of_id(tenant_factory.id.value)
