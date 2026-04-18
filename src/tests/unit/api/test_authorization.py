from deps_iam import constants
from deps_iam.domain.exceptions import IAMException


class TestAuthorization:
    endpoint = constants.API_PREFIX + "/authorize"

    def test__authorize__return_200(self, client, authorization_service_mock):
        authorization_service_mock.authorize.return_value = "deps_token"
        response = client.get(self.endpoint, headers={"authorization": "Bearer token"})
        assert response.status_code == 200

    def test__authorize__auth_token_header(self, client, authorization_service_mock):
        authorization_service_mock.authorize.return_value = "token"
        response = client.get(self.endpoint, headers={"authorization": "Bearer token"})
        assert response.headers["deps-token"] == "token"

    def test__authorize__return_400(self, client, authorization_service_mock):
        authorization_service_mock.authorize.side_effect = IAMException
        response = client.get(self.endpoint, headers={"authorization": "Bearer token"})
        assert response.status_code == 400
