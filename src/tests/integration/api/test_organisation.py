import json

import pytest

from deps_iam import constants
from deps_iam.domain.dtos import (
    InvitationSortingFieldEnum,
    UserListFilter,
    UserSortingFieldsEnum,
)
from deps_iam.domain.entities import Invitation
from deps_iam.infrastructure.access_management.context_vars import user
from tests.factories import UserFactory


@pytest.mark.usefixtures("add_user_to_organisation", "set_existing_user")
class TestOrganisation:
    endpoint = constants.API_PREFIX + "/organisations"

    def test_get__exists_list_organisation__return_200(self, client, organisation_factory, domain_services_accessor):
        for i in range(3):
            domain_services_accessor.organisation().create_organisation(organisation_factory())

        response = client.get(self.endpoint)
        response_content = response.json()

        assert response.status_code == 200
        assert len(response_content) == 4  # 3 from cycle and 1 from fixture add_user_to_organisation

    def test_create__new_organisation__return_201(self, client):
        organisation_name = "test_new_name"
        response = client.post(self.endpoint, json={"name": organisation_name})

        response_content = response.json()

        assert response.status_code == 201
        assert response_content["name"] == organisation_name

    def test_create__existing_organisation__return_409(self, client, organisation_factory, organisation_repository):
        organisation = organisation_factory()
        organisation_repository.create(organisation)
        response = client.post(self.endpoint, json={"pk": organisation.pk, "name": organisation.name})

        assert response.status_code == 409

    def test_create__new_organisation_missing_required_name__return_422(self, client):
        response = client.post(self.endpoint, json={})

        assert response.status_code == 422

    def test_get__not_existing_organisation__return_404(self, client):
        response = client.get(f"{self.endpoint}/111")

        assert response.status_code == 404

    def test_get__existing_organisation__return_200(
        self, client, organisation_factory, organisation_repository, add_user_to_organisation, existing_organisation
    ):
        response = client.get(f"{self.endpoint}/{existing_organisation.pk}")
        response_content = response.json()

        assert response.status_code == 200
        assert response_content["name"] == existing_organisation.name

    def test_delete__existing_organisation__return_200(
        self,
        client,
        organisation_factory,
        organisation_repository,
        add_user_to_organisation,
        existing_organisation,
    ):
        response = client.delete(f"{self.endpoint}/{existing_organisation.pk}")

        assert response.status_code == 200

        response_2 = client.get(f"{self.endpoint}/{existing_organisation.pk}")
        assert response_2.status_code == 404

    def test_delete__not_existing_organisation__return_403(self, client):
        response = client.delete(f"{self.endpoint}/11")

        assert response.status_code == 403

    @pytest.mark.parametrize("key,value", [("name", "CHANGED_NAME"), ("customizationUrl", "http://deps-customize")])
    def test_partial_update__existing_org__return_200(
        self,
        client,
        organisation_factory,
        organisation_repository,
        add_user_to_organisation,
        existing_organisation,
        key,
        value,
    ):
        response = client.patch(f"{self.endpoint}/{existing_organisation.pk}", json={key: value})

        assert response.status_code == 200
        assert response.json()[key] == value

    def test_partial_update__not_existing__org_return_404(self, client, add_user_to_organisation):
        response = client.patch(f"{self.endpoint}/abc", json={"name": "new_name"})

        assert response.status_code == 403

    def test_activate_user_org__existing_org__return_200(
        self, client, set_existing_user, add_user_to_organisation, entity_based_token
    ):
        new_org = client.post(
            self.endpoint,
            json={"name": "organisation_name"},
        ).json()
        response = client.post(f"{self.endpoint}/{new_org['pk']}/activate", headers={"deps-token": entity_based_token})

        assert response.status_code == 200
        assert response.json()["pk"] == new_org["pk"]

    def test_activate_org__not_existsting_org__raise_403(
        self, client, set_existing_user, add_user_to_organisation, entity_based_token
    ):
        response = client.post(f"{self.endpoint}/abracadabra/activate", headers={"deps-token": entity_based_token})
        assert response.status_code == 403

    def test_get_invitees__invitees_exist__return_list_of_invitees(
        self, client, set_existing_user, domain_services_accessor, organisation_factory
    ):
        org_service = domain_services_accessor.organisation()
        org = org_service.create_organisation(organisation_factory())
        usr = user.get()
        token = json.dumps({"subject": usr["subject"], "organisation": usr["organisation"]})

        email = "cool_user123@gmail.com"
        org_service.invite_users_to_organisation(usr["subject"], org.pk, [Invitation(email=email)])
        response = client.get(f"{self.endpoint}/{org.pk}/invitees", headers={"deps-token": token})

        resp_json = response.json()

        assert response.status_code == 200
        assert resp_json["meta"] == {"size": 1, "total": 1}
        assert resp_json["result"] == [{"email": email}]

    def test_get_invitees__invitees_exist__invited_by_another_member__return_list_of_invitees(
        self, client, domain_services_accessor, organisation_factory, user_repository, user_factory
    ):
        user = user_repository.add(user_factory())
        org_service = domain_services_accessor.organisation()
        org = org_service.create_organisation(organisation_factory())
        token = json.dumps({"subject": user.pk, "organisation": org.pk})

        email = "cool_user123@gmail.com"
        org_service.invite_users_to_organisation(user.pk, org.pk, [Invitation(email=email)])
        response = client.get(f"{self.endpoint}/{org.pk}/invitees", headers={"deps-token": token})

        resp_json = response.json()

        assert response.status_code == 200
        assert resp_json["meta"] == {"size": 1, "total": 1}
        assert resp_json["result"] == [{"email": email}]

    def test_get_invitees__no_invitees__empty_list_returned(
        self, client, domain_services_accessor, organisation_factory, user_repository, user_factory
    ):
        user = user_repository.add(user_factory())
        org_service = domain_services_accessor.organisation()
        org = org_service.create_organisation(organisation_factory())
        token = json.dumps({"subject": user.pk, "groups": [org.pk], "organisation": org.pk})

        response = client.get(f"{self.endpoint}/{org.pk}/invitees", headers={"deps-token": token})

        resp_json = response.json()

        assert response.status_code == 200
        assert resp_json["meta"] == {"size": 0, "total": 0}
        assert resp_json["result"] == []

    def test_get_invitees__search_email__correct_invitees_returned(
        self, client, domain_services_accessor, organisation_factory, user_repository, user_factory
    ):
        user = user_repository.add(user_factory())
        org_service = domain_services_accessor.organisation()
        org = org_service.create_organisation(organisation_factory())
        token = json.dumps({"subject": user.pk, "groups": [org.pk], "organisation": org.pk})

        invitations = [Invitation("testing@epam.com"), Invitation("test-me@epam.com"), Invitation("hello@gmail.com")]
        org_service.invite_users_to_organisation(user.pk, org.pk, invitations)

        response = client.get(f"{self.endpoint}/{org.pk}/invitees?email=test", headers={"deps-token": token})

        resp_json = response.json()

        assert response.status_code == 200
        assert resp_json["meta"] == {"size": 2, "total": 2}
        assert resp_json["result"] == [{"email": invitation.email} for invitation in invitations[:2]]

    @pytest.mark.parametrize("sorting_field", list(InvitationSortingFieldEnum))
    def test_get_invitees__sort_invitees__correct_order_returned(
        self, client, domain_services_accessor, organisation_factory, user_repository, user_factory, sorting_field
    ):
        user = user_repository.add(user_factory())
        org_service = domain_services_accessor.organisation()
        org = org_service.create_organisation(organisation_factory())
        token = json.dumps({"subject": user.pk, "groups": [org.pk], "organisation": org.pk})

        invitations = [Invitation("testing@epam.com"), Invitation("test-me@epam.com"), Invitation("hello@gmail.com")]
        org_service.invite_users_to_organisation(user.pk, org.pk, invitations)

        response = client.get(
            f"{self.endpoint}/{org.pk}/invitees?sortBy={sorting_field.value}", headers={"deps-token": token}
        )

        resp_json = response.json()

        invitations = invitations if sorting_field == InvitationSortingFieldEnum.email_desc else invitations[::-1]

        assert response.status_code == 200
        assert resp_json["result"] == [{"email": invitation.email} for invitation in invitations]

    @pytest.mark.parametrize("sorting_field", list(InvitationSortingFieldEnum))
    def test_get_invitees__sort_and_search_invitees__found_and_sorted_invitees(
        self, client, domain_services_accessor, organisation_factory, user_repository, user_factory, sorting_field
    ):
        user = user_repository.add(user_factory())
        org_service = domain_services_accessor.organisation()
        org = org_service.create_organisation(organisation_factory())
        token = json.dumps({"subject": user.pk, "groups": [org.pk], "organisation": org.pk})

        invitations = [Invitation("testing@epam.com"), Invitation("test-me@epam.com"), Invitation("hello@gmail.com")]
        org_service.invite_users_to_organisation(user.pk, org.pk, invitations)

        response = client.get(
            f"{self.endpoint}/{org.pk}/invitees?email=test&sortBy={sorting_field.value}", headers={"deps-token": token}
        )

        resp_json = response.json()

        invitations = (
            invitations[:2] if sorting_field == InvitationSortingFieldEnum.email_desc else invitations[:2][::-1]
        )

        assert response.status_code == 200
        assert resp_json["result"] == [{"email": invitation.email} for invitation in invitations]

    def test_invite_user_to_organisation__return_200(self, client, existing_organisation):
        response = client.post(f"{self.endpoint}/{existing_organisation.pk}/invite", json=[{"email": "test@test.com"}])

        assert response.status_code == 200

    def test_delete_user_from_organisation__return_200(
        self, client, existing_user, user_repository, organisation_repository, user_factory, existing_organisation
    ):
        another_user = user_repository.add(user_factory())
        organisation_repository.add_user_to_organisation(existing_organisation.pk, another_user.pk)

        response = client.request(
            "DELETE", f"{self.endpoint}/{existing_organisation.pk}/users", json={"users": [existing_user.pk]}
        )
        assert response.status_code == 200

    def test_delete_user_from_organisation__last_user__return_403(self, client, existing_user, existing_organisation):
        response = client.request(
            "DELETE", f"{self.endpoint}/{existing_organisation.pk}/users", json={"users": [existing_user.pk]}
        )
        assert response.status_code == 403

    def test_join_organisation__existing_org__return_200(self, client, entity_based_token):
        new_org = client.post(
            self.endpoint,
            json={"name": "organisation_name"},
        ).json()
        response = client.post(f"{self.endpoint}/{new_org['pk']}/join", headers={"deps-token": entity_based_token})

        assert response.status_code == 200
        assert response.json()["organisation"]["pk"] == new_org["pk"]

    def test_join_organisation__no_organisation__return_404(self, client, entity_based_token):
        response = client.post(f"{self.endpoint}/not_existent_org/join", headers={"deps-token": entity_based_token})

        assert response.status_code == 404

    @pytest.mark.usefixtures("add_users_to_organisation")
    def test_get_organisation_users__sorting_param__return_200(self, client, existing_organisation):
        query_params = "sortBy=firstName_lastName.desc"

        response = client.get(f"{self.endpoint}/{existing_organisation.pk}/users?{query_params}")

        assert response.status_code == 200

    @pytest.mark.usefixtures("add_users_to_organisation")
    def test_get_organisation_users__name_filter__return_200(self, client, existing_organisation):
        query_params = "firstName_lastName=Test Test"

        response = client.get(f"{self.endpoint}/{existing_organisation.pk}/users?{query_params}")

        assert response.json()["meta"] == {"size": 1, "total": 1}
        assert response.json()["result"][0]["pk"] == "1"
        assert response.status_code == 200

    def test_approve_user_request__return_200(
        self, client, organisation_repository, existing_organisation, user_repository, user_factory
    ):
        user = user_repository.add(user_factory())
        organisation_repository.create_approval_request(existing_organisation.pk, user.pk)

        response = client.post(f"{self.endpoint}/{existing_organisation.pk}/approve", json={"userPks": [user.pk]})

        assert response.status_code == 200

    def test_approve_user_request__no_request__return_404(
        self, client, existing_organisation, user_repository, user_factory
    ):
        user = user_repository.add(user_factory())

        response = client.post(f"{self.endpoint}/{existing_organisation.pk}/approve", json={"userPks": [user.pk]})

        assert response.status_code == 404

    def test_get_waiting_for_approvals__no_users__emtpy_list(self, client, existing_organisation):
        response = client.get(f"{self.endpoint}/{existing_organisation.pk}/approvals")

        resp_json = response.json()

        assert resp_json["result"] == []
        assert resp_json["meta"] == {"size": 0, "total": 0}
        assert response.status_code == 200

    def test_get_waiting_for_approvals__users_waiting__list_of_users_returned(
        self, client, existing_organisation, organisation_repository, user_repository
    ):
        users = []
        for u in UserFactory.build_batch(5):
            users.append(user_repository.add(u))
            organisation_repository.create_approval_request(existing_organisation.pk, u.pk)
        response = client.get(f"{self.endpoint}/{existing_organisation.pk}/approvals")

        resp_json = response.json()

        assert len(resp_json["result"]) == len(users)
        assert resp_json["meta"] == {"size": len(users), "total": len(users)}
        for u_entity, u_dict in zip(users, resp_json["result"]):
            assert u_entity.pk == u_dict["pk"]
            assert u_entity.email == u_dict["email"]
            assert u_entity.first_name == u_dict["firstName"]
            assert u_entity.last_name == u_dict["lastName"]
            assert u_entity.username == u_dict["username"]
            assert u_entity.created_at.isoformat() == u_dict["creationDate"]
            assert u_entity.organisation is None and u_dict["organisation"] is None
        assert response.status_code == 200

    def test_get_waiting_for_approvals__search_for_users__correct_users_returned(
        self, client, existing_organisation, organisation_repository, user_repository
    ):
        users = UserFactory.build_batch(2, first_name="test")

        for u in UserFactory.build_batch(3) + users:
            user_repository.add(u)
            organisation_repository.create_approval_request(existing_organisation.pk, u.pk)
        response = client.get(f"{self.endpoint}/{existing_organisation.pk}/approvals?firstName_lastName=test")

        resp_json = response.json()

        assert resp_json["meta"] == {"size": 2, "total": 2}
        assert all(u_entity.pk == u_dict["pk"] for u_entity, u_dict in zip(users, resp_json["result"]))

    @pytest.mark.parametrize("sort_field", list(UserSortingFieldsEnum))
    def test_get_waiting_for_approvals__sort_users__correct_order_returned(
        self, client, existing_organisation, organisation_repository, user_repository, sort_field
    ):
        users = UserFactory.build_batch(3)
        for idx, u in enumerate(users, 1):
            u.first_name = str(idx)
            user_repository.add(u)
            organisation_repository.create_approval_request(existing_organisation.pk, u.pk)

        response = client.get(f"{self.endpoint}/{existing_organisation.pk}/approvals?sortBy={sort_field.value}")

        resp_json = response.json()

        users = (
            users
            if sort_field == UserSortingFieldsEnum.full_name_asc
            else sorted(users, key=lambda u: u.first_name, reverse=True)
        )

        assert resp_json["result"][0]["firstName"] == users[0].first_name
        assert resp_json["result"][1]["firstName"] == users[1].first_name
        assert resp_json["result"][2]["firstName"] == users[2].first_name

    @pytest.mark.parametrize("sort_field", list(UserSortingFieldsEnum))
    def test_get_waiting_for_approvals__sort_and_search_users__correct_users_sorted(
        self, client, existing_organisation, organisation_repository, user_repository, sort_field
    ):
        users = UserFactory.build_batch(3, last_name="hello")
        for idx, u in enumerate(UserFactory.build_batch(3) + users, 1):
            u.first_name = str(idx)
            user_repository.add(u)
            organisation_repository.create_approval_request(existing_organisation.pk, u.pk)

        response = client.get(
            f"{self.endpoint}/{existing_organisation.pk}/approvals?sortBy={sort_field.value}&firstName_lastName=hello"
        )

        resp_json = response.json()

        users = (
            users
            if sort_field == UserSortingFieldsEnum.full_name_asc
            else sorted(users, key=lambda u: u.first_name, reverse=True)
        )

        assert resp_json["meta"] == {"size": len(users), "total": len(users)}
        assert resp_json["result"][0]["firstName"] == users[0].first_name
        assert resp_json["result"][1]["firstName"] == users[1].first_name
        assert resp_json["result"][2]["firstName"] == users[2].first_name

    def test_decline_user_request__return_200(
        self, client, organisation_repository, existing_organisation, user_repository, user_factory
    ):
        user = user_repository.add(user_factory())
        organisation_repository.create_approval_request(existing_organisation.pk, user.pk)

        response = client.request(
            "DELETE", f"{self.endpoint}/{existing_organisation.pk}/approvals", json={"userPks": [user.pk]}
        )

        assert response.status_code == 200

    def test_decline_user_request__no_request__return_404(
        self, client, existing_organisation, user_repository, user_factory
    ):
        user = user_repository.add(user_factory())

        response = client.request(
            "DELETE", f"{self.endpoint}/{existing_organisation.pk}/approvals", json={"userPks": [user.pk]}
        )

        assert response.status_code == 404

    def test_delete_invitees__user_was_invited__invitee_deleted(
        self, client, existing_organisation, existing_user, organisation_repository
    ):
        organisation_repository.invite_user_to_organisation(
            existing_user.pk, existing_organisation.pk, Invitation(email="test@mail.ru")
        )

        response = client.request(
            "DELETE", f"{self.endpoint}/{existing_organisation.pk}/invitees", json={"invitees": ["test@mail.ru"]}
        )

        assert response.status_code == 200

    def test_delete_invitees__user_was_not_invited__return_404(
        self, client, existing_organisation, existing_user, organisation_repository
    ):
        response = client.request(
            "DELETE",
            f"{self.endpoint}/{existing_organisation.pk}/invitees",
            json={"invitees": ["not-existing-email@hello.org"]},
        )

        assert response.status_code == 404


@pytest.mark.usefixtures("set_existing_user")
class TestOrganisationNoStartingOrg:
    endpoint = constants.API_PREFIX + "/organisations"

    def test_join_organisation__no_direct_invitation__approval_request_exists__return_403(
        self, client, create_approval_request, existing_organisation, entity_based_token
    ):
        response = client.post(
            f"{self.endpoint}/{existing_organisation.pk}/join", headers={"deps-token": entity_based_token}
        )

        assert response.status_code == 403
