import pytest

from deps_iam.constants import PERSONAL_ORGANISATION_POSTFIX
from deps_iam.domain.dtos import (
    InvitationListFilter,
    OrganisationListFilter,
    OrganisationTypesEnum,
    OrganisationUpdate,
    UserListFilter,
)
from deps_iam.domain.entities import Invitation
from deps_iam.domain.exceptions import (
    ApprovalRequestNotFoundError,
    InvitationNotFoundError,
    OrganisationAlreadyExistsError,
    OrganisationForbiddenError,
    OrganisationNotFoundError,
    UserOrganisationAlreadyExistsError,
    UserOrganisationNotFoundError,
)
from tests.factories import UserFactory


class TestOrganisationService:
    def test_create__new_organisation__return_organisation(self, organisation_service, organisation_factory):
        result = organisation_service.create_organisation(organisation_factory(name="abc"))

        assert result.name == "abc"

    def test_create__existing_organisation__raise_error(self, organisation_service, organisation_factory):
        organisation = organisation_factory()
        organisation_service.create_organisation(organisation)

        with pytest.raises(OrganisationAlreadyExistsError):
            organisation_service.create_organisation(organisation)

    def test_create__new_organisation__event_published(
        self, organisation_service, organisation_factory, produced_messages
    ):
        organisation_service.create_organisation(organisation_factory())

        assert len(produced_messages) == 2

    def test_get__exists_organisation__return_organisation(self, organisation_service, organisation_factory):
        organisation = organisation_factory()
        created_organisation = organisation_service.create_organisation(organisation)

        result = organisation_service.get_organisation(created_organisation.pk)

        assert organisation.name == result.name

    def test_get__not_existing_organisation__raise_error(self, organisation_service):
        with pytest.raises(OrganisationNotFoundError):
            organisation_service.get_organisation("-1")

    def test_get__list_organisation__return_list_organisation(self, organisation_service, organisation_factory):
        for i in range(3):
            organisation_service.create_organisation(organisation_factory())

        result = organisation_service.get_organisation_list(OrganisationListFilter())

        assert len(result) == 3

    def test_get__list_personal_organisation__return_list_organisation(
        self, organisation_service, organisation_factory
    ):
        for i in range(3):
            organisation_service.create_organisation(organisation_factory(name=PERSONAL_ORGANISATION_POSTFIX))

        for i in range(2):
            organisation_service.create_organisation(organisation_factory())

        result = organisation_service.get_organisation_list(
            OrganisationListFilter(organisation_type=OrganisationTypesEnum.PERSONAL)
        )

        assert len(result) == 3

    def test_get__list_non_personal_organisation__return_list_organisation(
        self, organisation_service, organisation_factory
    ):
        for i in range(3):
            organisation_service.create_organisation(organisation_factory(name=PERSONAL_ORGANISATION_POSTFIX))

        for i in range(2):
            organisation_service.create_organisation(organisation_factory())

        result = organisation_service.get_organisation_list(
            OrganisationListFilter(organisation_type=OrganisationTypesEnum.NON_PERSONAL)
        )

        assert len(result) == 2

    def test_get__empty_list_organisation__return_empty_list(self, organisation_service):
        result = organisation_service.get_organisation_list(OrganisationListFilter())

        assert result == []

    def test_delete__organisation__return_true(self, organisation_service, organisation_factory):
        created_organisation = organisation_service.create_organisation(organisation_factory())
        result = organisation_service.delete_organisation(created_organisation.pk)

        assert result is None

    def test_delete__not_existing_organisation__raise_error(self, organisation_service):
        with pytest.raises(OrganisationNotFoundError):
            organisation_service.delete_organisation("-1")

    def test_activate_user_org__correct_data__successful(
        self, add_user_to_organisation, organisation_service, existing_user, organisation_factory
    ):
        org = organisation_service.create_organisation(organisation_factory())
        organisation_service.add_user_to_organisation(org.pk, existing_user.pk)
        res = organisation_service.activate_user_organisation(org.pk, existing_user.pk)
        assert res == org

    def test_activate_user_org__incorrect_data__raise_error(self, organisation_service, existing_user):
        with pytest.raises(UserOrganisationNotFoundError):
            organisation_service.activate_user_organisation("abc", existing_user.pk)

    def test_activate_user_org__user_has_not_access_to_org__raise_error(
        self, organisation_service, add_user_to_organisation, existing_user, organisation_factory
    ):
        org = organisation_service.create_organisation(organisation_factory())
        with pytest.raises(UserOrganisationNotFoundError):
            organisation_service.activate_user_organisation(org.pk, existing_user.pk)

    def test_partial_update__org_exists__successful(self, organisation_service, organisation_factory):
        org = organisation_service.create_organisation(organisation_factory())
        new_name = "name"
        new_customization_url = "http://customize"
        changed_org = organisation_service.partial_update(
            org.pk, OrganisationUpdate(name=new_name, customization_url=new_customization_url)
        )

        assert changed_org.name == new_name
        assert changed_org.customization_url == new_customization_url

    def test_update_org_name__org_not_exists__raise_error(self, organisation_service):
        with pytest.raises(OrganisationNotFoundError):
            organisation_service.partial_update("1", OrganisationUpdate())

    def test_add_org_to_user__valid_data__successful(
        self, organisation_service, add_user_to_organisation, organisation_factory, existing_user
    ):
        org = organisation_service.create_organisation(organisation_factory())

        organisation_service.add_user_to_organisation(org.pk, existing_user.pk)

        assert org in organisation_service.get_organisation_list(OrganisationListFilter(user_pk=existing_user.pk))

    def test_add_org_to_user__existing_relation__raise_error(
        self, organisation_service, add_user_to_organisation, existing_organisation, existing_user
    ):
        with pytest.raises(UserOrganisationAlreadyExistsError):
            organisation_service.add_user_to_organisation(existing_organisation.pk, existing_user.pk)

    def test_get__organisation_users__return_list_users(
        self, organisation_repository, organisation_service, organisation_factory, users_service, user_factory
    ):
        created_organisation = organisation_service.create_organisation(organisation_factory())

        for i in range(3):
            users_service.add(user_factory(pk=i, organisation=created_organisation.pk))

        result = organisation_service.get_organisation_users(created_organisation.pk, UserListFilter())

        assert len(result.result) == 3

    def test_invite_user_to_organisation__user_exists__user_added_to_organisation(
        self, organisation_service, organisation_factory, user_factory, invitation_factory, existing_user, mocker
    ):
        org = organisation_service.create_organisation(organisation_factory())
        inviter = user_factory()
        organisation_service._publish_send_invitation_email_event = mocker.Mock()

        organisation_service.invite_users_to_organisation(
            inviter.pk, org.pk, [invitation_factory(email=existing_user.email)]
        )
        result = organisation_service.get_organisation_users(org.pk, UserListFilter())

        assert len(result.result) == 1
        assert result.result[0].email == existing_user.email

    def test_invite_user_to_organisation__user_exists_and_already_in_org__invitation_sent(
        self,
        organisation_service,
        users_service,
        existing_organisation,
        invitation_factory,
        mocker,
        monkeypatch,
        user_factory,
    ):
        org = existing_organisation
        inviter = users_service.add(user_factory())
        invitee = users_service.add(user_factory(email="coolest_email_ever@mail.org"))
        organisation_service.add_user_to_organisation(org.pk, invitee.pk)
        publish_mock = mocker.Mock()
        monkeypatch.setattr(organisation_service, "_publish_send_invitation_email_event", publish_mock)

        invitation = invitation_factory(email=invitee.email)
        organisation_service.invite_users_to_organisation(inviter.pk, org.pk, [invitation])

        publish_mock.assert_called_once_with(invitee.email, inviter.pk, org.pk)

    def test_invite_user_to_organisation__new_user_was_invited_twice__no_errors_raised(
        self, organisation_service, existing_organisation, invitation_factory, existing_user, mocker, monkeypatch
    ):
        org = existing_organisation
        inviter = existing_user
        publish_mock = mocker.Mock()
        monkeypatch.setattr(organisation_service, "_publish_send_invitation_email_event", publish_mock)

        invitation = invitation_factory()
        organisation_service.invite_users_to_organisation(inviter.pk, org.pk, [invitation])
        organisation_service.invite_users_to_organisation(inviter.pk, org.pk, [invitation])

        publish_mock.assert_has_calls(
            [mocker.call(invitation.email, inviter.pk, org.pk), mocker.call(invitation.email, inviter.pk, org.pk)]
        )

    def test_invite_user_to_organisation__new_user__user_added_to_invitees(
        self, organisation_service, organisation_factory, existing_user, invitation_factory
    ):
        org = organisation_service.create_organisation(organisation_factory())
        invitation = invitation_factory()

        organisation_service.invite_users_to_organisation(existing_user.pk, org.pk, [invitation])
        result = organisation_service.get_invitees(org.pk, InvitationListFilter())

        assert len(result.result) == 1
        assert result.result[0].email == invitation.email

    def test_invite_user_to_organisation__user_exists__invitation_email_event_published(
        self,
        existing_organisation,
        organisation_service,
        user_factory,
        existing_user,
        invitation_factory,
        produced_messages,
        users_service,
    ):
        invitation = invitation_factory(email=existing_user.email)
        inviter = users_service.add(user_factory(organisation=existing_organisation.pk))

        organisation_service.invite_users_to_organisation(inviter.pk, existing_organisation.pk, [invitation])

        assert len(produced_messages) == 1

    def test_invite_user_to_organisation__new_user__invitation_email_event_published(
        self, existing_organisation, organisation_service, existing_user, invitation_factory, produced_messages
    ):
        invitation = invitation_factory()
        organisation_service.invite_users_to_organisation(existing_user.pk, existing_organisation.pk, [invitation])
        assert len(produced_messages) == 1

    def test_join_organisation__no_organisation__raise_organisation_not_found(
        self, organisation_service, existing_user
    ):
        with pytest.raises(OrganisationNotFoundError):
            organisation_service.join_organisation("nonexistent_org_pk", existing_user.pk, existing_user.email)

    def test_join_organisation__already_in__success(
        self,
        organisation_service,
        add_user_to_organisation,
        existing_user,
        existing_organisation,
    ):
        new_user = organisation_service.join_organisation(
            existing_organisation.pk, existing_user.pk, existing_user.email
        )
        assert existing_user.organisation == new_user.organisation.pk

    def test_join_organisation__not_in__joined_from_direct_invitation__success(
        self, organisation_service, organisation_factory, invitation_factory, existing_user
    ):
        org = organisation_service.create_organisation(organisation_factory())
        invitation = invitation_factory(email=existing_user.email)
        organisation_service.invite_users_to_organisation(existing_user.pk, org.pk, [invitation])
        new_user = organisation_service.join_organisation(org.pk, existing_user.pk, existing_user.email)

        assert org.pk == new_user.organisation.pk

    def test_join_organisation__not_in__no_direct_invitation__approval_request_created__forbidden_raised(
        self, organisation_service, existing_organisation, existing_user
    ):
        with pytest.raises(OrganisationForbiddenError):
            organisation_service.join_organisation(existing_organisation.pk, existing_user.pk, existing_user.email)

    def test_join_organisation__not_in__no_direct_invitation__approval_request_exists__raise_organisation_forbidden(
        self, organisation_service, organisation_factory, organisation_repository, existing_user
    ):
        org = organisation_service.create_organisation(organisation_factory())
        organisation_repository.create_approval_request(org.pk, existing_user.pk)

        with pytest.raises(OrganisationForbiddenError):
            organisation_service.join_organisation(org.pk, existing_user.pk, existing_user.email)

    def test_delete_user_from_organisation__only_user__raise_error(
        self, organisation_service, existing_user, existing_organisation
    ):
        organisation_service.add_user_to_organisation(existing_organisation.pk, existing_user.pk)

        with pytest.raises(OrganisationForbiddenError):
            organisation_service.delete_user_from_organisation(existing_organisation.pk, [existing_user.pk])

    def test_delete_user_from_organisation__all_users__raise_error(
        self, users_service, user_factory, organisation_service, existing_organisation
    ):
        for i in range(3):
            users_service.add(user_factory(pk=i, organisation=existing_organisation.pk))

        with pytest.raises(OrganisationForbiddenError):
            organisation_service.delete_user_from_organisation(existing_organisation.pk, ["0", "1", "2"])

    def test_delete_user_from_organisation__user_deleted(
        self, users_service, user_factory, organisation_service, organisation_repository, existing_organisation
    ):
        for i in range(2):
            users_service.add(user_factory(pk=i, organisation=existing_organisation.pk))

        organisation_service.delete_user_from_organisation(existing_organisation.pk, ["0"])
        org_users = organisation_repository.get_organisation_users(existing_organisation.pk, UserListFilter())

        assert len(org_users) == 1

    def test_delete_user_from_organisation__other_organisation_activated(
        self,
        users_service,
        user_repository,
        user_factory,
        organisation_service,
        organisation_factory,
        existing_organisation,
    ):
        org2 = organisation_service.create_organisation(organisation_factory())

        for i in range(2):
            users_service.add(user_factory(pk=i, organisation=existing_organisation.pk))

        organisation_service.add_user_to_organisation(org2.pk, "0")
        organisation_service.delete_user_from_organisation(existing_organisation.pk, ["0"])

        user = user_repository.get("0")

        assert user.organisation == org2.pk

    def test_delete_user_from_organisation__has_no_org__org_deactivated(
        self, users_service, user_factory, user_repository, organisation_service, existing_organisation
    ):
        for i in range(2):
            users_service.add(user_factory(pk=i, organisation=existing_organisation.pk))

        organisation_service.delete_user_from_organisation(existing_organisation.pk, ["0"])
        user = user_repository.get("0")

        assert user.organisation is None

    def test_approve_user_request__success(
        self, existing_user, organisation_repository, organisation_service, existing_organisation
    ):
        organisation_repository.create_approval_request(existing_organisation.pk, existing_user.pk)
        organisation_service.approve_user_request(existing_organisation.pk, [existing_user.pk])

        org_users = organisation_service.get_organisation_users(existing_organisation.pk, UserListFilter())

        assert org_users.result[0].pk == existing_user.pk
        assert org_users.result[0].organisation == existing_organisation.pk

    def test_get_waiting_for_approvals__no_users_empty_list_returned(
        self, organisation_service, existing_organisation, organisation_repository
    ):
        res = organisation_service.get_waiting_for_approvals(existing_organisation.pk, UserListFilter())

        assert res.result == []
        assert res.meta.size == 0
        assert res.meta.total == 0

    def test_get_waiting_for_approvals__users_waiting__list_of_users_returned(
        self, organisation_service, organisation_repository, existing_organisation, user_repository
    ):
        users = []
        for u in UserFactory.build_batch(5):
            users.append(user_repository.add(u))
            organisation_repository.create_approval_request(existing_organisation.pk, u.pk)

        result = organisation_service.get_waiting_for_approvals(existing_organisation.pk, UserListFilter())

        assert result.result == users
        assert result.meta.size == len(users)
        assert result.meta.total == len(users)

    def test_invite_to_organisation__user_is_waiting_for_approval__approval_request_deleted(
        self, organisation_service, organisation_repository, existing_user, existing_organisation
    ):
        organisation_repository.create_approval_request(existing_organisation.pk, existing_user.pk)

        organisation_service.invite_users_to_organisation(
            existing_user.pk, existing_organisation.pk, [Invitation(email=existing_user.email)]
        )

        with pytest.raises(ApprovalRequestNotFoundError):
            organisation_repository.delete_approval_request(existing_organisation.pk, existing_user.pk)

    def test_decline_user_request__request_deleted(
        self, existing_user, organisation_repository, organisation_service, existing_organisation
    ):
        organisation_repository.create_approval_request(existing_organisation.pk, existing_user.pk)
        organisation_service.decline_user_request(existing_organisation.pk, [existing_user.pk])

        result = organisation_service.get_waiting_for_approvals(existing_organisation.pk, UserListFilter())

        assert result.result == []
        assert result.meta.total == 0

    def test_decline_user_request__user_not_in_org(
        self, existing_user, organisation_repository, organisation_service, existing_organisation
    ):
        organisation_repository.create_approval_request(existing_organisation.pk, existing_user.pk)
        organisation_service.decline_user_request(existing_organisation.pk, [existing_user.pk])

        org_users = organisation_service.get_organisation_users(existing_organisation.pk, UserListFilter())

        assert len(org_users.result) == 0

    def test_delete_invitees__user_was_invited__invitee_deleted(
        self, existing_user, organisation_repository, organisation_service, existing_organisation
    ):
        organisation_repository.invite_user_to_organisation(
            existing_user.pk, existing_organisation.pk, Invitation(email="test@mail.ru")
        )
        organisation_service.delete_invitees(existing_organisation.pk, ["test@mail.ru"])

        invitees = organisation_service.get_invitees(existing_organisation.pk, InvitationListFilter())

        assert len(invitees.result) == 0

    def test_delete_invitees__user_was_not_ivited__not_found_is_raised(self, organisation_service):
        with pytest.raises(InvitationNotFoundError):
            organisation_service.delete_invitees("test-pk", ["test@mail.ru"])
