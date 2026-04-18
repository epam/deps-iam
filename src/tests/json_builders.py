from deps_iam.domain.dtos import ExpandedUser


def build_expanded_user_json(expanded_user: ExpandedUser):
    organisation = None
    if expanded_user.organisation:
        organisation = {
            "pk": expanded_user.organisation.pk,
            "name": expanded_user.organisation.name,
            "customizationUrl": expanded_user.organisation.customization_url,
        }

    return {
        "pk": expanded_user.pk,
        "creationDate": expanded_user.created_at.isoformat(),
        "username": expanded_user.username,
        "email": expanded_user.email,
        "firstName": expanded_user.first_name,
        "lastName": expanded_user.last_name,
        "organisation": organisation,
        "defaultCustomizationUrl": expanded_user.default_customization_url,
    }
