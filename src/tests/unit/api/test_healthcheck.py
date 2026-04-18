from deps_iam import constants


class TestHealthcheck:
    endpoint = constants.BASE_API_PREFIX

    def test_healthcheck_endpoint__return_200(self, client, postgres_datasource_mock):
        postgres_datasource_mock.healthcheck.return_value = ""
        response = client.get(f"{self.endpoint}/healthcheck")
        assert response.status_code == 200
