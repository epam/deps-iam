from deps_iam.api.v1 import router as v1_router
from deps_iam.api.v2 import router as v2_router

from .debug import debug_router
from .healthcheck import healthcheck_router
from .service_info import service_info_router
