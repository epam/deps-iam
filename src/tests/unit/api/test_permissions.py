from deps_iam import constants
from deps_iam.domain.entities import PermissionEntity


class TestPermissionView:
    endpoint = f"{constants.API_PREFIX}/permissions"

    def test_get__return_proper_response_fields_value(self, client, permission_service_mock):
        permission_name = "Test permission"
        permission_service_mock.get_list.return_value = [PermissionEntity(permission_name)]
        expected_json = [permission_name]

        response = client.get(self.endpoint)
        response_json = response.json()

        assert response.status_code == 200
        assert response_json == expected_json
