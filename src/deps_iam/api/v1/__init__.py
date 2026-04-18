from fastapi import APIRouter

from deps_iam.api.v1.authorization import auth_router
from deps_iam.api.v1.organisation import organisation_router
from deps_iam.api.v1.permissions import permissions_router
from deps_iam.api.v1.roles import roles_router
from deps_iam.api.v1.users import users_router

router = APIRouter()

router.include_router(permissions_router)
router.include_router(users_router)
router.include_router(organisation_router)
router.include_router(roles_router)
router.include_router(auth_router)
