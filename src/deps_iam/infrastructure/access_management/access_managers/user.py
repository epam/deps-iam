from typing import Optional

from deps_iam.extras.value_objects import UserValueObject
from deps_iam.infrastructure.access_management.context_vars import user


class CurrentUserMixin:
    @property
    def current_user(self) -> Optional[UserValueObject]:
        user_credentials = user.get(None)
        if user_credentials:
            return UserValueObject(**user_credentials)

        return None
