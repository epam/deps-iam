from .auth import AccessTokenAuthServiceError, AuthError
from .base import AlreadyExistsError, ForbiddenError, IAMException, NotFoundError
from .invitation import IncorrectEmailException
from .organisation import (
    ApprovalRequestAlreadyExistsError,
    ApprovalRequestNotFoundError,
    InvitationAlreadyExistsError,
    InvitationNotFoundError,
    OrganisationAlreadyExistsError,
    OrganisationForbiddenError,
    OrganisationNotFoundError,
    UserOrganisationAlreadyExistsError,
    UserOrganisationNotFoundError,
)
from .permission import PermissionAlreadyExistsError, PermissionNotFoundError
from .registration import RegisterError
from .role import RoleAlreadyExistsError, RoleNotFoundError
from .tenant import TenantNotFoundError
from .user import UserAlreadyExistsError, UserNotFoundError
from .user_api_key import UserApiKeyNotFoundError
