from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Query, status

from deps_iam.api.models import (
    ApproveUserResponseModel,
    DeclineUserRequestResponseModel,
    DeleteUserResponseModel,
    ExpandedUserModel,
    InvitationModel,
    ListDataModel,
    ListMetaDataModel,
    OrganisationModel,
    OrganisationUpdateModel,
    UserListFilterRequestModel,
    UserModel,
)
from deps_iam.containers import DomainServiceAccessors
from deps_iam.domain.dtos import (
    InvitationListFilter,
    InvitationSortingFieldEnum,
    OrganisationListFilter,
)
from deps_iam.domain.entities import OrganisationPk
from deps_iam.domain.exceptions import ForbiddenError, UserOrganisationNotFoundError
from deps_iam.domain.interfaces.services import IOrganisationService
from deps_iam.infrastructure.access_management.context_vars import user

from ..endpoint_marker import MarkerRoute
from ..endpoint_visibility import Visibility

organisation_router = APIRouter(prefix="/organisations", route_class=MarkerRoute)

tags = ["Organisations"]


@organisation_router.get(
    "",
    response_model=list[OrganisationModel],
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_user_organisations(
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    return organisation_service.get_organisation_list(OrganisationListFilter())


@organisation_router.get(
    "/{organisation_pk}",
    response_model=OrganisationModel,
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_organisation_by_pk(
    organisation_pk: OrganisationPk,
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    return organisation_service.get_organisation(pk=organisation_pk)


@organisation_router.post(
    "",
    response_model=OrganisationModel,
    tags=tags,
    status_code=status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def create_organisation(
    organisation_entity: OrganisationModel,
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    return organisation_service.create_organisation(organisation_entity.to_domain())


@organisation_router.delete(
    "/{organisation_pk}",
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_organisation(
    organisation_pk: OrganisationPk,
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    return organisation_service.delete_organisation(organisation_pk)


@organisation_router.patch(
    "/{organisation_pk}",
    response_model=OrganisationModel,
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def patch_organisation(
    organisation_pk: OrganisationPk,
    organisation_update_model: OrganisationUpdateModel,
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    return organisation_service.partial_update(organisation_pk, organisation_update_model.to_domain())


@organisation_router.post(
    "/{organisation_pk}/activate",
    response_model=OrganisationModel,
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def activate_user_organisation(
    organisation_pk: OrganisationPk,
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    try:
        user_pk = user.get()["subject"]
        return organisation_service.activate_user_organisation(organisation_pk, user_pk)
    except UserOrganisationNotFoundError:
        raise ForbiddenError(f"Current user hasn't access to organisation {organisation_pk}.")


@organisation_router.get(
    "/{organisation_pk}/users",
    response_model=ListDataModel[UserModel],
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_organisation_users(
    organisation_pk: OrganisationPk,
    users_filters: UserListFilterRequestModel = Depends(),
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    organisation_users = organisation_service.get_organisation_users(organisation_pk, users_filters.to_domain())
    return ListDataModel(
        meta=ListMetaDataModel(size=organisation_users.meta.size, total=organisation_users.meta.total),
        result=[
            UserModel.model_validate(user_entity).model_dump(
                include={"pk", "created_at", "first_name", "last_name", "email"}, by_alias=True
            )
            for user_entity in organisation_users.result
        ],
    )


@organisation_router.get(
    "/{organisation_pk}/invitees",
    response_model=ListDataModel[InvitationModel],
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_invitees(
    organisation_pk: OrganisationPk,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, alias="perPage"),
    search_term: str | None = Query(None, alias="email"),
    sort_by: InvitationSortingFieldEnum = Query(InvitationSortingFieldEnum.email_desc, alias="sortBy"),
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    filtering = InvitationListFilter(
        page=page,
        per_page=per_page,
        sorting_field=sort_by,
        search_term=search_term,
    )
    invitees = organisation_service.get_invitees(organisation_pk, filtering)
    meta = ListMetaDataModel(total=invitees.meta.total, size=invitees.meta.size)
    return ListDataModel(meta=meta, result=invitees.result)


@organisation_router.delete(
    "/{organisation_pk}/invitees",
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_invitees(
    organisation_pk: OrganisationPk,
    invitees: list[str] = Body(..., embed=True),
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    organisation_service.delete_invitees(organisation_pk, invitees)


@organisation_router.post(
    "/{organisation_pk}/invite",
    response_model=list[InvitationModel],
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def invite_user_to_organisation(
    organisation_pk: OrganisationPk,
    invitations: list[InvitationModel],
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    inviter_pk = user.get()["subject"]
    return organisation_service.invite_users_to_organisation(
        inviter_pk, organisation_pk, invitations=[invitation.to_domain() for invitation in invitations]
    )


@organisation_router.post(
    "/{organisation_pk}/join",
    response_model=ExpandedUserModel,
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def join_organisation(
    organisation_pk: OrganisationPk,
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    user_credentials = user.get()
    user_pk = user_credentials["subject"]
    user_email = user_credentials["email"]
    return ExpandedUserModel.model_validate(
        organisation_service.join_organisation(organisation_pk, user_pk, user_email)
    )


@organisation_router.delete(
    "/{organisation_pk}/users",
    response_model=DeleteUserResponseModel,
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_user_from_organisation(
    organisation_pk: OrganisationPk,
    user_pks: list[str] = Body(..., alias="users", min_length=1, embed=True),
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    deleted_users = organisation_service.delete_user_from_organisation(organisation_pk, user_pks)
    return DeleteUserResponseModel(deleted_users=deleted_users)


@organisation_router.post(
    "/{organisation_pk}/approve",
    response_model=ApproveUserResponseModel,
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def approve_user_request(
    organisation_pk: OrganisationPk,
    user_pks: list[str] = Body(..., alias="userPks", min_length=1, embed=True),
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    approved_users = organisation_service.approve_user_request(organisation_pk, user_pks)
    return ApproveUserResponseModel(approved_users=approved_users)


@organisation_router.get(
    "/{organisation_pk}/approvals",
    response_model=ListDataModel[UserModel],
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_list_of_waiting_for_approval_users(
    organisation_pk: OrganisationPk,
    filtering: UserListFilterRequestModel = Depends(),
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    users = organisation_service.get_waiting_for_approvals(organisation_pk, filtering.to_domain())
    meta = ListMetaDataModel(total=users.meta.total, size=users.meta.size)
    return ListDataModel(meta=meta, result=[UserModel.model_validate(u) for u in users.result])


@organisation_router.delete(
    "/{organisation_pk}/approvals",
    response_model=DeclineUserRequestResponseModel,
    tags=tags,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def decline_user_request(
    organisation_pk: OrganisationPk,
    user_pks: list[str] = Body(..., alias="userPks", min_length=1, embed=True),
    organisation_service: IOrganisationService = Depends(Provide[DomainServiceAccessors.organisation]),
):
    declined_users = organisation_service.decline_user_request(organisation_pk, user_pks)
    return DeclineUserRequestResponseModel(declined_users=declined_users)
