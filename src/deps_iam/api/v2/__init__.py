from fastapi import APIRouter

from deps_iam.api.v2.authorization import authorization_router

router = APIRouter()

router.include_router(authorization_router)
