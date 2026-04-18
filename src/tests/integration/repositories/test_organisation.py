import random

import pytest

from deps_iam.domain.dtos import (
    InvitationListFilter,
    InvitationSortingFieldEnum,
    OrganisationListFilter,
    OrganisationUpdate,
    UserListFilter,
    UserSortingFieldsEnum,
)
from deps_iam.domain.dtos.organisation import EMPTY
from deps_iam.domain.entities import Invitation
from deps_iam.domain.exceptions import (
    ApprovalRequestAlreadyExistsError,
    ApprovalRequestNotFoundError,
    InvitationAlreadyExistsError,
    InvitationNotFoundError,
    OrganisationAlreadyExistsError,
    OrganisationNotFoundError,
    UserOrganisationAlreadyExistsError,
    UserOrganisationNotFoundError,
)
from tests.factories import UserFactory


def assert_organisations_without_id(org1, org2):
    assert org1.name == org2.name
    assert org1.customization_url == org2.customization_url


class TestOrganisationEntityRepositoryCRUD:
    def test_create__new_organisation__return_organisation(self, organisation_repository, organisation_factory):
        organisation = organisation_factory()
        result = organisation_repository.create(organisation)

        assert_organisations_without_id(result, organisation)

    def test_create__existing_organisation__raise_error(self, organisation_repository, organisation_factory):
        organisation = organisation_factory()
        organisation_repository.create(organisation)
        with pytest.raises(OrganisationAlreadyExistsError):
            organisation_repository.create(organisation)

    def test_get__exists_organisation__return_organisation(self, organisation_repository, organisation_factory):
        organisation = organisation_factory()
        created_organisation = organisation_repository.create(organisation)
        result = organisation_repository.get(created_organisation.pk)

        assert_organisations_without_id(result, organisation)

    def test_get__not_existing_organisation__raise_error(self, organisation_repository):
        with pytest.raises(OrganisationNotFoundError):
            organisation_repository.get("123")

    def test_get__list_organisation__return_list_organisation(self, organisation_repository, organisation_factory):
        for i in range(3):
            organisation_repository.create(organisation_factory())

        result = organisation_repository.get_list()

        assert len(result) == 3

    def test_get__not_existing_list_organisation__return_empty_list(self, organisation_repository):
        result = organisation_repository.get_list()

        assert result == []

    def test_delete__exists_organisation__return_true(self, organisation_repository, organisation_factory):
        created_organisation = organisation_repository.create(organisation_factory())

        result = organisation_repository.delete(created_organisation.pk)

        assert result is None

    def test_delete__not_existing_organisation__raise_error(self, organisation_repository):
        with pytest.raises(OrganisationNotFoundError):
            organisation_repository.delete("-1")

    def test_get_by_name__org_exists__org_returned(self, organisation_repository, organisation_factory):
        org = organisation_repository.create(organisation_factory())

        same_org = organisation_repository.get_by_name(org.name)

        assert org == same_org

    def test_get_by_name__org_does_not_exist__not_found_error(self, organisation_repository, organisation_factory):
        with pytest.raises(OrganisationNotFoundError):
            organisation_repository.get_by_name("fix this goddamn door")

    @pytest.mark.parametrize(
        "field,value",
        (
            ("name", ""),
            ("name", "name_two"),
            ("name", EMPTY),
            ("customization_url", ""),
            ("customization_url", "url_two"),
            ("customization_url", None),
            ("customization_url", EMPTY),
        ),
    )
    def test_update_org__org_exists__successful(self, organisation_repository, organisation_factory, field, value):
        org = organisation_repository.create(organisation_factory(name="name_one", customization_url="url_one"))
        org_update = OrganisationUpdate(**{field: value})
        organisation_repository.partial_update(org.pk, org_update)

        expected = value
        if value is EMPTY:
            expected = getattr(org, field)
        assert getattr(organisation_repository.get(org.pk), field) == expected

    def test_update__org_not_exist__raise_error(self, organisation_repository, organisation_factory):
        with pytest.raises(OrganisationNotFoundError):
            organisation_repository.partial_update("1", organisation_factory())

    def test_add_org_to_user__valid_data__successful(
        self, organisation_repository, organisation_factory, user_repository, user_factory
    ):
        user = user_repository.add(user_factory())
        org = organisation_repository.create(organisation_factory())

        organisation_repository.add_user_to_organisation(org.pk, user.pk)

        assert org in organisation_repository.get_list(OrganisationListFilter(user_pk=user.pk))

    def test_add_org_to_user__existing_relation__raise_error(
        self, organisation_repository, organisation_factory, user_repository, user_factory
    ):
        user = user_repository.add(user_factory())
        org = organisation_repository.create(organisation_factory())
        organisation_repository.add_user_to_organisation(org.pk, user.pk)

        with pytest.raises(UserOrganisationAlreadyExistsError):
            organisation_repository.add_user_to_organisation(org.pk, user.pk)

    def test_get__organisation_users_list__return_list_users(
        self, organisation_repository, organisation_factory, user_repository, user_factory
    ):
        org = organisation_repository.create(organisation_factory())

        for _ in range(3):
            user = user_repository.add(user_factory())
            organisation_repository.add_user_to_organisation(org.pk, user.pk)

        result = organisation_repository.get_organisation_users(org.pk, UserListFilter())

        assert len(result) == 3

    def test_get__organisation_users_list__return_empty_list_users(self, organisation_repository, organisation_factory):
        org = organisation_repository.create(organisation_factory())

        result = organisation_repository.get_organisation_users(org.pk, UserListFilter())

        assert result == []

    def test_get_invitees__no_invitees__empty_list(self, organisation_repository):
        assert organisation_repository.get_invitees("test", InvitationListFilter()) == []

    def test_get_invitees__user_added_invitees__invitees_returned(
        self,
        organisation_repository,
        user_repository,
        user_factory,
        organisation_factory,
    ):
        user = user_repository.add(user_factory())
        org = organisation_repository.create(organisation_factory())

        email = "hello@outlook.com"

        organisation_repository.invite_user_to_organisation(user.pk, org.pk, Invitation(email=email))

        invitees = organisation_repository.get_invitees(org.pk, InvitationListFilter(user_pk=user.pk))

        assert invitees[0].email == email

    def test_get_invitees__search_email__correct_invitees_returned(
        self,
        organisation_repository,
        user_repository,
        user_factory,
        organisation_factory,
    ):
        user = user_repository.add(user_factory())
        org = organisation_repository.create(organisation_factory())

        invitations = [
            Invitation(email="not-me@epam.com"),
            Invitation(email="test-email@gmail.com"),
            Invitation(email="testing@epam.com"),
        ]

        for invitation in invitations:
            organisation_repository.invite_user_to_organisation(user.pk, org.pk, invitation)

        invitees = organisation_repository.get_invitees(org.pk, InvitationListFilter(search_term="test"))

        assert len(invitees) == 2
        assert invitees == invitations[1:]

    @pytest.mark.parametrize("sorting_field", list(InvitationSortingFieldEnum))
    def test_get_invitees__sort_invitees__invitations_returned_in_correct_order(
        self,
        organisation_repository,
        user_repository,
        user_factory,
        organisation_factory,
        sorting_field,
    ):
        user = user_repository.add(user_factory())
        org = organisation_repository.create(organisation_factory())

        invitations = [Invitation(email="a@epam.com"), Invitation(email="b@gmail.com")]
        for invitation in invitations:
            organisation_repository.invite_user_to_organisation(user.pk, org.pk, invitation)

        invitees = organisation_repository.get_invitees(org.pk, InvitationListFilter(sorting_field=sorting_field))
        invitations = invitations if sorting_field == InvitationSortingFieldEnum.email_asc else invitations[::-1]

        assert len(invitees) == 2
        assert invitees == invitations

    def test_get_total_invitees_count__total_count_returned(
        self,
        organisation_repository,
        user_repository,
        user_factory,
        organisation_factory,
    ):
        user = user_repository.add(user_factory())
        org = organisation_repository.create(organisation_factory())

        email = "second@outlook.com"

        organisation_repository.invite_user_to_organisation(user.pk, org.pk, Invitation(email=email))

        count = organisation_repository.get_total_invitees_count(org.pk, InvitationListFilter(user_pk=user.pk))

        assert count == 1

    def test_invite_user_to_organisation__new_user__add_user_to_invitees(
        self, organisation_repository, user_repository, user_factory, organisation_factory, invitation_factory
    ):
        inviter = user_repository.add(user_factory())
        invitation = invitation_factory()

        org = organisation_repository.create(organisation_factory())
        organisation_repository.invite_user_to_organisation(inviter.pk, org.pk, invitation)
        invitees = organisation_repository.get_invitees(org.pk, InvitationListFilter())

        assert invitees[0].email == invitation.email
        assert len(invitees) == 1

    def test_invite_user_to_organisation_existing_invitation_raise_error(
        self, organisation_repository, user_repository, user_factory, organisation_factory, invitation_factory
    ):
        inviter = user_repository.add(user_factory())
        invitation = invitation_factory()
        org = organisation_repository.create(organisation_factory())

        organisation_repository.invite_user_to_organisation(inviter.pk, org.pk, invitation)
        with pytest.raises(InvitationAlreadyExistsError):
            organisation_repository.invite_user_to_organisation(inviter.pk, org.pk, invitation)

    def test_delete_invitation__exists__return_none(
        self, organisation_repository, user_repository, user_factory, organisation_factory, invitation_factory
    ):
        inviter = user_repository.add(user_factory())
        invitation = invitation_factory()
        org = organisation_repository.create(organisation_factory())

        organisation_repository.invite_user_to_organisation(inviter.pk, org.pk, invitation)

        assert organisation_repository.delete_invitation(org.pk, invitation.email) is None

    def test_delete_invitation__not_exists__raise_invitation_not_found(self, organisation_repository):
        with pytest.raises(InvitationNotFoundError):
            organisation_repository.delete_invitation("non_existent_org_pk", "non_existent_email")

    def test_create_approval_request__not_exists__return_approval_request(
        self, organisation_repository, organisation_factory, user_repository, user_factory
    ):
        org = organisation_repository.create(organisation_factory())
        user = user_repository.add(user_factory())
        approval_request = organisation_repository.create_approval_request(org.pk, user.pk)

        assert approval_request.organisation_pk == org.pk
        assert approval_request.user_pk == user.pk

    def test_create_approval_request__exists__raise_approval_request_already_exists(
        self, organisation_repository, organisation_factory, user_repository, user_factory
    ):
        org = organisation_repository.create(organisation_factory())
        user = user_repository.add(user_factory())
        organisation_repository.create_approval_request(org.pk, user.pk)

        with pytest.raises(ApprovalRequestAlreadyExistsError):
            organisation_repository.create_approval_request(org.pk, user.pk)

    def test_delete_user_from_organisation_exists__user_deleted(
        self, user_repository, user_factory, organisation_repository, organisation_factory
    ):
        user = user_repository.add(user_factory())
        org = organisation_repository.create(organisation_factory())

        organisation_repository.add_user_to_organisation(org.pk, user.pk)

        result = organisation_repository.delete_user_from_organisation(org.pk, user.pk)
        assert result == user.pk

    def test_delete_user_from_organisation_not_exist__raise_error(self, organisation_repository, organisation_factory):
        org = organisation_repository.create(organisation_factory())

        with pytest.raises(UserOrganisationNotFoundError):
            organisation_repository.delete_user_from_organisation(org.pk, "user_not_in_org_pk")

    def test_delete_approval_request__request_exists__deleted(
        self, user_repository, user_factory, organisation_repository, organisation_factory
    ):
        user = user_repository.add(user_factory())
        org = organisation_repository.create(organisation_factory())
        organisation_repository.create_approval_request(org.pk, user.pk)

        result = organisation_repository.delete_approval_request(org.pk, user.pk)

        assert result == user.pk

    def test_delete_approval_request__not_exist__raise_error(
        self, user_repository, user_factory, organisation_repository, organisation_factory
    ):
        user = user_repository.add(user_factory())
        org = organisation_repository.create(organisation_factory())

        with pytest.raises(ApprovalRequestNotFoundError):
            organisation_repository.delete_approval_request(org.pk, user.pk)


@pytest.mark.usefixtures("add_users_to_organisation")
class TestOrganisationUsersGetByFilter:
    def test_get_organisation_users__sort_asc__return_sorted_users(
        self, organisation_repository, existing_organisation
    ):
        result = organisation_repository.get_organisation_users(
            existing_organisation.pk, UserListFilter(sort_field=UserSortingFieldsEnum.full_name_asc)
        )

        assert all(
            (
                result[0].pk == "1",
                result[1].pk == "3",
                result[2].pk == "2",
            )
        )

    def test_get_organisation_users__sort_desc__return_sorted_users(
        self, organisation_repository, existing_organisation
    ):
        result = organisation_repository.get_organisation_users(
            existing_organisation.pk, UserListFilter(sort_field=UserSortingFieldsEnum.full_name_desc)
        )

        assert all(
            (
                result[0].pk == "2",
                result[1].pk == "3",
                result[2].pk == "1",
            )
        )

    def test_get_organisation_users__name_filter__return_users(self, organisation_repository, existing_organisation):
        result = organisation_repository.get_organisation_users(
            existing_organisation.pk, UserListFilter(full_name="TestTest")
        )

        assert result[0].pk == "1"
        assert len(result) == 1

    def test_get_waiting_for_approvals__no_users__empty_list_returned(
        self, organisation_repository, existing_organisation
    ):
        result = organisation_repository.get_waiting_for_approvals(existing_organisation.pk, UserListFilter())
        assert result == []

    def test_get_waiting_for_approvals__users_waiting__list_of_users_returned(
        self, organisation_repository, existing_organisation, user_repository
    ):
        users = []
        for u in UserFactory.build_batch(5):
            users.append(user_repository.add(u))
            organisation_repository.create_approval_request(existing_organisation.pk, u.pk)

        result = organisation_repository.get_waiting_for_approvals(existing_organisation.pk, UserListFilter())
        assert result == users

    def test_get_total_approvals_count__users_waiting__correct_count_returned(
        self, organisation_repository, existing_organisation, user_repository
    ):
        users = []
        for u in UserFactory.build_batch(random.randint(1, 5)):
            users.append(user_repository.add(u))
            organisation_repository.create_approval_request(existing_organisation.pk, u.pk)

        count = organisation_repository.get_total_approvals_count(existing_organisation.pk, UserListFilter())
        assert count == len(users)

    def test_get_total_approvals_count__search_for_users__correct_count_returned(
        self, organisation_repository, existing_organisation, user_repository
    ):
        u = UserFactory(first_name="test", last_name="search")
        users = UserFactory.build_batch(random.randint(1, 5)) + [u]
        for u in users:
            user_repository.add(u)
            organisation_repository.create_approval_request(existing_organisation.pk, u.pk)

        count = organisation_repository.get_total_approvals_count(
            existing_organisation.pk, UserListFilter(full_name="search")
        )
        assert count == 1

    def test_get_waiting_for_approval__search_for_user__correct_user_returned(
        self, organisation_repository, existing_organisation, user_repository
    ):
        u = UserFactory(first_name="test", last_name="search")
        users = UserFactory.build_batch(random.randint(1, 5)) + [u]
        for u in users:
            user_repository.add(u)
            organisation_repository.create_approval_request(existing_organisation.pk, u.pk)

        approvals = organisation_repository.get_waiting_for_approvals(
            existing_organisation.pk, UserListFilter(full_name="search")
        )
        assert approvals[0] == u
