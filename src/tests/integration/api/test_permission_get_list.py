class TestPermissionsAPI:
    def test_get_permissions_list(self, client):
        response = client.get("/api/iam/v1/permissions")
        response_json = response.json()

        assert response.status_code == 200
        assert isinstance(response_json, list)
