import pytest

from deps_iam.infrastructure.access_management.context_vars import user


@pytest.fixture
def org_access_manager(domain_service_access_managers):
    return domain_service_access_managers.organisation()


@pytest.fixture
def org_access_service(domain_services_accessor):
    return domain_services_accessor.organisation()
