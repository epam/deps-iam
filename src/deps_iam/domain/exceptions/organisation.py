from .base import AlreadyExistsError, ForbiddenError, NotFoundError


class OrganisationNotFoundError(NotFoundError):
    code = "organisation_not_found"


class OrganisationAlreadyExistsError(AlreadyExistsError):
    code = "organisation_already_exists"


class OrganisationForbiddenError(ForbiddenError):
    code = "organisation_forbidden_error"


class UserOrganisationAlreadyExistsError(AlreadyExistsError):
    code = "user_organisation_already_exists"


class UserOrganisationNotFoundError(NotFoundError):
    code = "user_organisation_not_found"


class InvitationAlreadyExistsError(AlreadyExistsError):
    code = "invitation_already_exists"


class InvitationNotFoundError(NotFoundError):
    code = "invitation_not_found"


class ApprovalRequestAlreadyExistsError(AlreadyExistsError):
    code = "approval_request_already_exists"


class ApprovalRequestNotFoundError(NotFoundError):
    code = "approval_request_not_found"
