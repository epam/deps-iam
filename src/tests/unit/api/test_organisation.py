import urllib.parse
from http import HTTPStatus
from typing import Any, Dict
from unittest.mock import patch

import pytest

from deps_iam import constants
from deps_iam.api.models import DeleteUserResponseModel, UserModel
from deps_iam.domain.dtos import ListDataObject, ListMetaDataObject
from deps_iam.domain.entities import Invitation
from deps_iam.domain.exceptions import (
    ApprovalRequestNotFoundError,
    InvitationNotFoundError,
    OrganisationAlreadyExistsError,
    OrganisationForbiddenError,
    OrganisationNotFoundError,
)
from deps_iam.extras.auth.deps_auth import DepsAuthService
from tests.factories import UserFactory, UserListDataFactory
from tests.factories.common import ListMetaDataFactory


@pytest.fixture
def deps_auth_authorize_mock():
    with patch.object(DepsAuthService, "authorize") as authorize:
        yield authorize


class TestOrganisationView:
    endpoint = f"{constants.API_PREFIX}/organisations"

    def test_get__not_existing_organisation_id__return_404(self, client, organisation_service_mock):
        organisation_service_mock.get_organisation.side_effect = OrganisationNotFoundError

        response = client.get(self.endpoint + "undefined")

        assert response.status_code == 404

    def test_get__existing_organisation_id__return_200(self, client, organisation_factory, org_services_accessor_mock):
        org_services_accessor_mock.get_organisation.return_value = organisation_factory()

        response = client.get(self.endpoint + "/1")

        assert response.status_code == 200

    def test_delete__not_existing_organisation_id__return_404(self, client, org_services_accessor_mock):
        org_services_accessor_mock.delete_organisation.side_effect = OrganisationNotFoundError

        response = client.delete(self.endpoint + "undefined")

        assert response.status_code == 404

    def test_delete__existing_organisation_id__return_200(self, client, org_services_accessor_mock):
        org_services_accessor_mock.delete_organisation.return_value = True

        response = client.delete(self.endpoint + "/1")

        assert response.status_code == 200

    def test_get__empty_organisation_list__return_200(self, client, org_services_accessor_mock):
        org_services_accessor_mock.get_organisation_list.return_value = []

        response = client.get(self.endpoint)

        assert response.status_code == 200

    def test_get__organisation_list__return_200(self, client, org_services_accessor_mock, organisation_factory):
        org_services_accessor_mock.get_organisation_list.return_value = [organisation_factory()]

        response = client.get(self.endpoint)

        assert response.status_code == 200

    def test_create__new_organisation__return_201(self, client, org_services_accessor_mock, organisation_factory):
        organisation = organisation_factory()
        org_services_accessor_mock.create_organisation.return_value = organisation

        response = client.post(self.endpoint, json={"name": organisation.name})

        assert response.status_code == 201

    def test_create__existing_organisation__return_409(self, client, org_services_accessor_mock):
        org_services_accessor_mock.create_organisation.side_effect = OrganisationAlreadyExistsError

        response = client.post(self.endpoint, json={"name": "existing_name"})

        assert response.status_code == 409

    def test_update_org__existing_org__return_200(self, client, org_services_accessor_mock, organisation_factory):
        org = organisation_factory()
        org_services_accessor_mock.partial_update.return_value = org

        response = client.patch(
            f"{self.endpoint}/{org.pk}", json={"name": "new_name", "customizationUrl": "http://customize"}
        )

        assert response.status_code == 200

    def test_update_org_name__not_existing_org__return_404(self, client, org_services_accessor_mock):
        org_services_accessor_mock.partial_update.side_effect = OrganisationNotFoundError

        response = client.patch(f"{self.endpoint}/1", json={"name": "new_name"})

        assert response.status_code == 404

    def test_activate_user_org__existing_org__return_200(
        self,
        client,
        org_services_accessor_mock,
        organisation_factory,
        deps_auth_authorize_mock,
    ):
        deps_auth_authorize_mock.authorize.return_value = {"subject": "avc"}
        org = organisation_factory()
        org_services_accessor_mock.activate_user_organisation.return_value = org

        response = client.post(
            f"{self.endpoint}/{org.pk}/activate",
        )

        assert response.status_code == 200

    def test_activate_user_org__not_existing_org__return_403(
        self,
        client,
        deps_auth_authorize_mock,
        org_services_accessor_mock,
    ):
        deps_auth_authorize_mock.authorize.return_value = {"subject": "avc"}
        org_services_accessor_mock.activate_user_organisation.side_effect = OrganisationForbiddenError

        response = client.post(f"{self.endpoint}/123/activate")

        assert response.status_code == 403

    def test_get__users_of_organisation__return_200(self, client, org_services_accessor_mock):
        org_services_accessor_mock.get_organisation_users.return_value = UserListDataFactory()

        response = client.get(self.endpoint + "/deps-users/users")

        assert response.status_code == 200

    def test_get__users_of_organisation__return_proper_fields(self, client, org_services_accessor_mock):
        org_services_accessor_mock.get_organisation_users.return_value = UserListDataFactory()

        response = client.get(self.endpoint + "/deps-users/users")
        response_json = response.json()

        assert "result" in response_json
        assert "meta" in response_json
        assert "total" in response_json["meta"]
        assert "size" in response_json["meta"]

    def test_get__users_of_organisation__return_proper_fields_values(self, client, org_services_accessor_mock):
        users = [
            UserFactory(pk="1"),
            UserFactory(pk="2"),
            UserFactory(pk="a"),
        ]
        meta_info = ListMetaDataFactory(total=5, size=7)
        user_list = UserListDataFactory(meta=meta_info, result=users)

        org_services_accessor_mock.get_organisation_users.return_value = user_list
        response = client.get(f"{self.endpoint}/deps-users/users")
        response_json = response.json()

        assert len(response_json["result"]) == 3
        assert response_json["meta"]["total"] == 5
        assert response_json["meta"]["size"] == 7

    def test_get__users_of_organisation__with_valid_filters__return_200(self, client, org_services_accessor_mock):
        filters = self._build_filters()
        query_params = self._build_query_params(filters)

        org_services_accessor_mock.get_organisation_users.return_value = UserListDataFactory()
        response = client.get(f"{self.endpoint}/deps-users/users?{query_params}")

        assert response.status_code == 200

    def test_get__users_of_organisation__invalid_page__return_422(self, client, org_services_accessor_mock):
        filters = self._build_filters()
        filters["page"] = "one"
        query_params = self._build_query_params(filters)

        org_services_accessor_mock.get_organisation_users.return_value = UserListDataFactory()
        response = client.get(f"{self.endpoint}/deps-users/users?{query_params}")

        assert response.status_code == 422

    def test_get__users_of_organisation__invalid_per_page__return_422(self, client, org_services_accessor_mock):
        filters = self._build_filters()
        filters["perPage"] = "two"
        query_params = self._build_query_params(filters)

        org_services_accessor_mock.get_organisation_users.return_value = UserListDataFactory()
        response = client.get(f"{self.endpoint}/deps-users/users?{query_params}")

        assert response.status_code == 422

    @staticmethod
    def _build_filters() -> Dict[str, Any]:
        return {
            "page": 1,
            "perPage": 2,
        }

    @staticmethod
    def _build_query_params(filters: Dict[str, Any]) -> str:
        return urllib.parse.urlencode(filters)

    def test_get_invitees__list_of_invited_emails_returned(
        self,
        client,
        deps_auth_authorize_mock,
        org_services_accessor_mock,
    ):
        deps_auth_authorize_mock.authorize.return_value = {"subject": "avc"}
        org_services_accessor_mock.get_invitees.return_value = ListDataObject(
            meta=ListMetaDataObject(size=2, total=10),
            result=[Invitation(email="test@gmail.com"), Invitation(email="test@outlook.com")],
        )

        response = client.get(f"{self.endpoint}/123/invitees")

        resp_json = response.json()

        assert response.status_code == 200
        assert resp_json["result"] == [{"email": "test@gmail.com"}, {"email": "test@outlook.com"}]
        assert resp_json["meta"] == {"total": 10, "size": 2}

    @pytest.mark.parametrize("email", ["Test.Email1234@outlook.com", "test@Epam.com"])
    def test_invite_user__correct_email__200_returned(
        self,
        client,
        deps_auth_authorize_mock,
        org_services_accessor_mock,
        email,
    ):
        deps_auth_authorize_mock.authorize.return_value = {"subject": "avc"}
        org_services_accessor_mock.invite_users_to_organisation.return_value = [Invitation(email)]

        invitations = [{"email": email}]
        response = client.post(f"{self.endpoint}/deps-users/invite", json=invitations)

        assert response.status_code == HTTPStatus.OK
        assert response.json() == [{"email": email.lower()}]

    @pytest.mark.parametrize("forbidden_symbol", list(",#=+<>%\|/;()[]''\"\"`` @") + [".."])
    def test_invite_user__incorrect_email__400_returned(
        self,
        client,
        deps_auth_authorize_mock,
        forbidden_symbol,
    ):
        deps_auth_authorize_mock.authorize.return_value = {"subject": "avc"}

        email = f"test.email{forbidden_symbol}hey@outlook.com"
        invitations = [{"email": email}]
        response = client.post(f"{self.endpoint}/deps-users/invite", json=invitations)

        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_invite_user_to_organisation__return_200(
        self, client, org_services_accessor_mock, organisation_factory, invitation_factory
    ):
        org = organisation_factory()
        invitation = invitation_factory()

        org_services_accessor_mock.invite_users_to_organisation.return_value = [invitation]

        response = client.post(f"{self.endpoint}/{org.pk}/invite", json=[{"email": "test@test.com"}])

        assert response.status_code == 200

    def test_join_organisation__existing_org__return_200(self, client, org_services_accessor_mock):
        user = UserFactory()
        org_services_accessor_mock.join_organisation.return_value = user

        response = client.post(f"{self.endpoint}/random_org_pk/join")

        assert response.json()["pk"] == user.pk
        assert response.status_code == 200

    def test_join_organisation__no_organisation__return_404(self, client, org_services_accessor_mock):
        org_services_accessor_mock.join_organisation.side_effect = OrganisationNotFoundError

        response = client.post(f"{self.endpoint}/random_org_pk/join")

        assert response.status_code == 404

    def test_join_organisation__approval_request_exists__return_403(self, client, org_services_accessor_mock):
        org_services_accessor_mock.join_organisation.side_effect = OrganisationForbiddenError

        response = client.post(f"{self.endpoint}/random_org_pk/join")

        assert response.status_code == 403

    def test_delete_user_from_organisation__return_200(self, client, org_services_accessor_mock):
        org_services_accessor_mock.delete_user_from_organisation.return_value = ["user_pk"]

        response = client.request("DELETE", f"{self.endpoint}/org_name/users", json={"users": ["user_pk"]})

        assert response.status_code == 200

    def test_delete_last_user_from_organisation__return_403(self, client, org_services_accessor_mock):
        org_services_accessor_mock.delete_user_from_organisation.side_effect = OrganisationForbiddenError

        response = client.request("DELETE", f"{self.endpoint}/org_name/users", json={"users": ["last_user_pk"]})

        assert response.status_code == 403

    def test_get_organisation_users__sort_desc__return_200(self, client, org_services_accessor_mock):
        query_params = "sortBy=firstName_lastName.desc"
        org_services_accessor_mock.get_organisation_users.return_value = UserListDataFactory()

        response = client.get(f"{self.endpoint}/deps-users/users?{query_params}")

        assert response.status_code == 200

    def test_get_organisation_users__invalid_sorting_param__return_422(self, client):
        query_params = "sortBy=asdf"

        response = client.get(f"{self.endpoint}/deps-users/users?{query_params}")

        assert response.status_code == 422

    def test_approve_user_request__return_200(self, client, org_services_accessor_mock):
        org_services_accessor_mock.approve_user_request.return_value = ["user_pk"]

        response = client.post(f"{self.endpoint}/deps-users/approve", json={"userPks": ["user_pk"]})

        assert response.status_code == 200

    def test_approve_user_request__not_exist__return_404(self, client, org_services_accessor_mock):
        org_services_accessor_mock.approve_user_request.side_effect = ApprovalRequestNotFoundError

        response = client.post(f"{self.endpoint}/deps-users/approve", json={"userPks": ["user_pk"]})

        assert response.status_code == 404

    def test_get_waiting_for_approvals__correct_request__return_200(self, client, org_services_accessor_mock):
        user = UserFactory()
        org_services_accessor_mock.get_waiting_for_approvals.return_value = ListDataObject(
            result=[user], meta=ListMetaDataObject(size=1, total=1)
        )
        response = client.get(f"{self.endpoint}/deps-users/approvals")

        response_json = response.json()

        assert response.status_code == 200
        assert response_json["meta"] == {"size": 1, "total": 1}
        assert user.pk == response_json["result"][0]["pk"]

    def test_decline_user_request__return_200(self, client, org_services_accessor_mock):
        org_services_accessor_mock.decline_user_request.return_value = ["user_pk"]

        response = client.request("DELETE", f"{self.endpoint}/deps-users/approvals", json={"userPks": ["user_pk"]})

        assert response.status_code == 200

    def test_decline_user_request__not_exist__return_404(self, client, org_services_accessor_mock):
        org_services_accessor_mock.decline_user_request.side_effect = ApprovalRequestNotFoundError

        response = client.request("DELETE", f"{self.endpoint}/deps-users/approvals", json={"userPks": ["user_pk"]})

        assert response.status_code == 404

    def test_delete_invitees__user_deleted__return_200(self, client, org_services_accessor_mock):
        response = client.request("DELETE", f"{self.endpoint}/deps-users/invitees", json={"invitees": ["test@mail.ru"]})

        assert response.status_code == 200

    def test_delete_invitees__not_exist__return_404(self, client, org_services_accessor_mock):
        org_services_accessor_mock.delete_invitees.side_effect = InvitationNotFoundError

        response = client.request("DELETE", f"{self.endpoint}/deps-users/invitees", json={"invitees": ["test@mail.ru"]})

        assert response.status_code == 404
