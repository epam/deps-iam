import pytest
from pytest import raises

from deps_iam.domain.dtos import (
    OrganisationListFilter,
    OrganisationUpdate,
    UserListFilter,
)
from deps_iam.domain.exceptions import (
    ApprovalRequestAlreadyExistsError,
    ApprovalRequestNotFoundError,
    InvitationNotFoundError,
    OrganisationAlreadyExistsError,
    OrganisationForbiddenError,
    OrganisationNotFoundError,
    UserNotFoundError,
    UserOrganisationNotFoundError,
)
from tests.factories import InvitationFactory, UserFactory
from tests.factories.user import ExpandedUserFactory


@pytest.fixture
def organisation_service(services):
    services.organisation.reset_override()
    yield services.organisation()


class TestOrganisationService:
    def test_create__new_organisation__successfully(
        self, organisation_repository_mock, organisation_factory, organisation_service, mocker
    ):
        organisation = organisation_factory()
        organisation_repository_mock.create.return_value = organisation
        mocker.patch.object(organisation_service._uow, "event_publisher", autospec=True)

        response = organisation_service.create_organisation(organisation)

        assert response == organisation

    def test_create__existing_organisation__raise_error(
        self, organisation_repository_mock, organisation_factory, organisation_service
    ):
        organisation_repository_mock.create.side_effect = OrganisationAlreadyExistsError

        with raises(OrganisationAlreadyExistsError):
            organisation_service.create_organisation(organisation_factory)

    def test_delete__existing_organisation__success(self, organisation_service, organisation_repository_mock):
        organisation_repository_mock.delete.return_value = True
        response = organisation_service.delete_organisation(1)

        assert response is True

    def test_delete__not_existing_organisation__raise_error(self, organisation_service, organisation_repository_mock):
        organisation_repository_mock.delete.side_effect = OrganisationNotFoundError

        with pytest.raises(OrganisationNotFoundError):
            organisation_service.delete_organisation(1)

    def test_get__exists_list_organisation__success(
        self, organisation_service, organisation_repository_mock, organisation_factory
    ):
        organisation_list = [organisation_factory() for i in range(3)]
        organisation_repository_mock.get_list.return_value = organisation_list

        response = organisation_service.get_organisation_list(OrganisationListFilter())

        assert response == organisation_list

    def test_get__empty_list_organisation__return_empty_list(self, organisation_service, organisation_repository_mock):
        organisation_repository_mock.get_list.return_value = []

        response = organisation_service.get_organisation_list(OrganisationListFilter())

        assert response == []

    def test_partial_update__repository_called(
        self, organisation_service, organisation_repository_mock, organisation_factory, org_services_accessor_mock
    ):
        new_name = "new_name"
        organisation_repository_mock.partial_update.return_value = organisation_factory(name=new_name)

        organisation_service.partial_update("1", OrganisationUpdate())

        organisation_repository_mock.partial_update.assert_called_once()

    def test_update_org_name__not_existing_org_raise_error(self, organisation_service, organisation_repository_mock):
        organisation_repository_mock.partial_update.side_effect = OrganisationNotFoundError

        with pytest.raises(OrganisationNotFoundError):
            organisation_service.partial_update(1, "new_name")

    def test_add_org_to_user__valid_data__success(self, organisation_service, organisation_repository_mock):
        organisation_repository_mock.add_user_to_organisation.return_value = None

        organisation_service.add_user_to_organisation("1", "1")

    def test_add_org_to_user__invalid_data__raise_error(self, organisation_service, organisation_repository_mock):
        organisation_repository_mock.add_user_to_organisation.side_effect = UserOrganisationNotFoundError

        with pytest.raises(UserOrganisationNotFoundError):
            organisation_service.add_user_to_organisation("1", "1")

    def test_get__organisation_users__exists_list_users__success(
        self, organisation_service, organisation_repository_mock
    ):
        user_list = [UserFactory(pk=i) for i in range(3)]
        organisation_repository_mock.get_organisation_users.return_value = user_list

        response = organisation_service.get_organisation_users("deps-users", UserListFilter())

        assert response.result == user_list

    def test_get__organisation_users__empty_list_users__return_empty_list(
        self, organisation_service, organisation_repository_mock
    ):
        organisation_repository_mock.get_organisation_users.return_value = []

        response = organisation_service.get_organisation_users("deps-users", UserListFilter())

        assert response.result == []

    def test_join_organisation__no_organisation__raise_organisation_not_found(
        self, organisation_service, organisation_repository_mock
    ):
        user = UserFactory()
        org_pk = "not_existent_org_pk"

        organisation_repository_mock.get_list.return_value = []
        organisation_repository_mock.get.side_effect = OrganisationNotFoundError

        with pytest.raises(OrganisationNotFoundError):
            organisation_service.join_organisation(org_pk, user.pk, user.email)

    def test_join_organisation__already_in__success(
        self, organisation_service, organisation_repository_mock, user_service_mock, organisation_factory
    ):
        org = organisation_factory()
        user = ExpandedUserFactory(organisation=org)

        organisation_repository_mock.get_list.return_value = [org]
        user_service_mock.get_expanded_user.return_value = user

        assert organisation_service.join_organisation(org.pk, user.pk, user.email) == user

    def test_join_organisation__not_in__joined_from_direct_invitation__success(
        self, organisation_service, organisation_repository_mock, user_service_mock, organisation_factory
    ):
        org = organisation_factory()
        user = ExpandedUserFactory(organisation=org)

        organisation_repository_mock.get_list.side_effect = [[], [org]]
        user_service_mock.get_expanded_user.return_value = user

        assert organisation_service.join_organisation(org.pk, user.pk, user.email) == user

    def test_join_organisation__not_in__no_direct_invitation__approval_request_created__forbidden_raised(
        self, organisation_service, organisation_repository_mock, user_service_mock, organisation_factory
    ):
        org = organisation_factory()
        user = ExpandedUserFactory(organisation=org)

        organisation_repository_mock.get_list.side_effect = [[], [org]]
        organisation_repository_mock.delete_invitation.side_effect = InvitationNotFoundError
        user_service_mock.get_expanded_user.return_value = user

        with pytest.raises(OrganisationForbiddenError):
            organisation_service.join_organisation(org.pk, user.pk, user.email)

    def test_join_organisation__not_in__no_direct_invitation__approval_request_exists__raise_organisation_forbidden(
        self, organisation_service, organisation_repository_mock, user_service_mock, organisation_factory
    ):
        org = organisation_factory()
        user = ExpandedUserFactory(organisation=org)

        organisation_repository_mock.get_list.side_effect = [[], [org]]
        organisation_repository_mock.delete_invitation.side_effect = InvitationNotFoundError
        organisation_repository_mock.create_approval_request.side_effect = ApprovalRequestAlreadyExistsError
        user_service_mock.get_expanded_user.return_value = user

        with pytest.raises(OrganisationForbiddenError):
            organisation_service.join_organisation(org.pk, user.pk, user.email)

    def test_delete_user_from_organisation_exists__success(
        self, organisation_service, organisation_repository_mock, mocker
    ):
        deleted_user_pk = UserFactory().pk
        organisation_repository_mock.delete_user_from_organisation.return_value = deleted_user_pk
        mocker.patch.object(organisation_service, "_is_all_users_deletion", return_value=False)

        response = organisation_service.delete_user_from_organisation("org_name", [deleted_user_pk])

        assert response == [deleted_user_pk]

    def test_delete_user_from_organisation_not_exist__raise_error(
        self, organisation_service, organisation_repository_mock, mocker
    ):
        organisation_repository_mock.delete_user_from_organisation.side_effect = UserOrganisationNotFoundError
        mocker.patch.object(organisation_service, "_is_all_users_deletion", return_value=False)

        with pytest.raises(UserOrganisationNotFoundError):
            organisation_service.delete_user_from_organisation("org_name", ["user_pk"])

    def test_approve_user_request__success(
        self, organisation_service, organisation_factory, user_factory, organisation_repository_mock, mocker
    ):
        approved_user_pk = user_factory().pk
        org = organisation_factory()
        organisation_repository_mock.delete_approval_request.return_value = approved_user_pk
        mocker.patch.object(organisation_service, "activate_user_organisation", return_value=org)

        response = organisation_service.approve_user_request(org.pk, [approved_user_pk])

        assert response == [approved_user_pk]

    def test_approve_user_request__not_exist__raise_error(self, organisation_service, organisation_repository_mock):
        organisation_repository_mock.delete_approval_request.side_effect = ApprovalRequestNotFoundError

        with pytest.raises(ApprovalRequestNotFoundError):
            organisation_service.approve_user_request("org_pk", ["user_pk"])

    def test_get_waiting_for_approvals__list_of_users_returned(
        self, organisation_service, organisation_repository_mock
    ):
        user = UserFactory()
        organisation_repository_mock.get_total_approvals_count.return_value = 1
        organisation_repository_mock.get_waiting_for_approvals.return_value = [user]
        users = organisation_service.get_waiting_for_approvals("deps-users", OrganisationListFilter())

        assert users.meta.size == 1
        assert users.meta.total == 1
        assert users.result[0] == user

    def test_decline_user_request__success(
        self, organisation_service, organisation_factory, user_factory, organisation_repository_mock
    ):
        declined_user_pk = user_factory().pk
        org = organisation_factory()
        organisation_repository_mock.delete_approval_request.return_value = declined_user_pk

        response = organisation_service.decline_user_request(org.pk, [declined_user_pk])

        assert response == [declined_user_pk]

    def test_decline_user_request__not_exist__raise_error(self, organisation_service, organisation_repository_mock):
        organisation_repository_mock.delete_approval_request.side_effect = ApprovalRequestNotFoundError

        with pytest.raises(ApprovalRequestNotFoundError):
            organisation_service.decline_user_request("org_pk", ["user_pk"])

    def test_delete_invitees__not_exists__raise_error(self, organisation_service, organisation_repository_mock):
        organisation_repository_mock.delete_invitation.side_effect = InvitationNotFoundError

        with pytest.raises(InvitationNotFoundError):
            organisation_service.delete_invitees("org_pk", ["test@mail.ru"])

    def test_invite_user_to_organisation__user_has_been_invited_once__no_errors_raised(
        self, organisation_service, organisation_repository_mock, user_repository_mock, monkeypatch, mocker
    ):
        user_repository_mock.get_user_by_email.side_effect = UserNotFoundError
        organisation_repository_mock.get_invitees.return_value = []

        mock_publish = mocker.Mock()
        monkeypatch.setattr(organisation_service, "_publish_send_invitation_email_event", mock_publish)
        organisation_service.invite_users_to_organisation("test-user-pk", "test-org-pk", [InvitationFactory()])
        mock_publish.assert_called_once()

    def test_invite_user_to_organisation__user_has_been_invited_twice__no_errors_raised(
        self, organisation_service, organisation_repository_mock, user_repository_mock, monkeypatch, mocker
    ):
        user_repository_mock.get_user_by_email.side_effect = UserNotFoundError
        organisation_repository_mock.get_invitees.return_value = [InvitationFactory()]

        mock_publish = mocker.Mock()
        monkeypatch.setattr(organisation_service, "_publish_send_invitation_email_event", mock_publish)
        organisation_service.invite_users_to_organisation("test-user-pk", "test-org-pk", [InvitationFactory()])
        mock_publish.assert_called_once()

    def test_invite_user_to_organisation__user_exists_but_not_in_org__invitation_sent(
        self,
        organisation_service,
        organisation_repository_mock,
        user_repository_mock,
        monkeypatch,
        user_factory,
        mocker,
    ):
        user = user_factory()
        user_repository_mock.get_user_by_email.return_value = user
        organisation_repository_mock.get_organisation_users.return_value = []
        org_pk = "test-org-pk"

        mock_publish = mocker.Mock()
        monkeypatch.setattr(organisation_service, "_publish_send_invitation_email_event", mock_publish)
        organisation_service.invite_users_to_organisation(user.pk, org_pk, [InvitationFactory()])

        organisation_repository_mock.add_user_to_organisation.assert_called_once_with(org_pk, user.pk)
        mock_publish.assert_called_once()

    def test_invite_user_to_organisation__user_already_in_organisation__invitation_sent(
        self,
        organisation_service,
        organisation_repository_mock,
        user_repository_mock,
        monkeypatch,
        user_factory,
        mocker,
    ):
        user = user_factory()
        user_repository_mock.get_user_by_email.return_value = user
        organisation_repository_mock.get_organisation_users.return_value = [user]

        mock_publish = mocker.Mock()
        monkeypatch.setattr(organisation_service, "_publish_send_invitation_email_event", mock_publish)
        organisation_service.invite_users_to_organisation(user.pk, "test-org-pk", [InvitationFactory()])

        organisation_repository_mock.add_user_to_organisation.assert_not_called()
        mock_publish.assert_called_once()
