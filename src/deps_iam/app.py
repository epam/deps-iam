import logging
import os
from typing import Awaitable, Callable

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import Response

from deps_iam import api, application, auth, constants, events_handler
from deps_iam.api.middleware.cache import CacheMiddleware
from deps_iam.containers import Application
from deps_iam.domain.exceptions import AuthError
from deps_iam.error_handlers import json_domain_error_handler, register_error_handler
from deps_iam.extras.fastapi_utils import add_auth_to_openapi
from deps_iam.infrastructure.access_management.context_vars import user
from deps_iam.maga_containers import Application as MagaApplication
from deps_iam.settings import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_application() -> Application:
    settings = Settings()
    app = Application(messaging_driver_settings=settings.messaging_driver_settings)
    app.config.from_pydantic(settings)
    app.init_resources()

    app.message_brokers.broker_client().user_context = user
    app.messaging.transactional_outbox_producer().user_context = user

    if app.config.instrumentation_enabled():
        from deps_observability_instrumentation import (  # noqa: WPS433
            instrument_messaging,
            setup_instrumentation,
        )

        setup_instrumentation()
        instrument_messaging(app.messaging.producer(), app.messaging.consumer())
        logger.info("Instrumentation enabled.")

    app.services.wire(packages=(api,))
    app.infrastructure_services.wire(packages=(api,))
    app.domain_service_accessors.wire(packages=(api,))
    app.wire(packages=(api, events_handler))
    app.datasources.wire((api.healthcheck,))
    app.core.wire((api.service_info,))

    return app


def init_maga_application() -> MagaApplication:
    settings = Settings()
    app = MagaApplication(messaging_driver_settings=settings.messaging_driver_settings)
    app.config.from_pydantic(settings)
    app.init_resources()
    app.services.wire(packages=(api, application))
    app.wire(packages=(api, application))

    return app


def create_fastapi() -> FastAPI:
    app: Application = init_application()

    fastapi_app = FastAPI(
        title=constants.PROJECT_NAME,
        version=app.config.version(),
        docs_url=f"{constants.API_PREFIX}{constants.SWAGGER_DOC_URL}" if app.config.documentation_enabled() else None,
        description=constants.DESCRIPTION,
        openapi_url=f"{constants.API_PREFIX}/openapi.json" if app.config.documentation_enabled() else None,
    )
    fastapi_app.include_router(api.debug_router, prefix=constants.BASE_API_PREFIX)
    fastapi_app.include_router(api.healthcheck_router, prefix=constants.BASE_API_PREFIX)
    fastapi_app.include_router(api.v1_router, prefix=constants.API_PREFIX)
    fastapi_app.include_router(api.v2_router, prefix=constants.V2_API_PREFIX)
    fastapi_app.include_router(api.service_info_router, prefix=constants.BASE_API_PREFIX)
    fastapi_app.app = app

    register_error_handler(fastapi_app)
    add_auth_to_openapi(fastapi_app)

    register_auth(fastapi_app)
    if app.config.cache_settings.enabled():
        fastapi_app.add_middleware(CacheMiddleware, settings=app.config.cache_settings())
        logger.info("CACHING ENABLED!")

    return fastapi_app


def register_auth(app: FastAPI):
    @app.middleware("http")
    async def handle_authorization(  # noqa: WPS430
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            auth.set_user_from_deps_token(request)
        except AuthError as err:
            return json_domain_error_handler(err, err.status_code)
        return await call_next(request)


def run_api():
    options = {
        "host": "0.0.0.0",  # noqa: S104
        "port": 8000,
        "log_level": "debug",
        "reload": os.getenv("ENV") == "local",
    }

    uvicorn.run("deps_iam.app:create_fastapi", **options)


def run_polling_publisher():
    app = init_application()

    logger.info("Polling publisher has been enabled")
    app.messaging.polling_publisher().run_polling()
    logger.info("Polling publisher has been disabled")


def run_consumer() -> None:
    app = init_application()

    consumer = app.services.consumer()
    consumer.start_consuming()


def run_initialization() -> None:
    app: Application = init_application()

    logger.info("Started process for tenant creation with adding users.")

    app.services.initialization().create_tenant_with_users()

    logger.info("Finished process for tenant creation with adding users.")
