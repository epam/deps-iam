from deps_iam.domain.dtos import ExpandedUser


class CustomizationService:
    # Temporary class to support old flow of using one customization url for everyone
    def __init__(self, default_customization_url: str):
        self._default_customization_url = default_customization_url

    def enrich_customization_settings_for_user(self, expanded_user: ExpandedUser):
        expanded_user.default_customization_url = self._default_customization_url
