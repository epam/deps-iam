import logging
from http import HTTPStatus
from json import JSONDecodeError

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request

from deps_iam.api.models import ErrorModel
from deps_iam.domain.exceptions import (
    AlreadyExistsError,
    ForbiddenError,
    IAMException,
    NotFoundError,
)
from deps_iam.extras.auth.exceptions import DepsAuthError

logger = logging.getLogger(__name__)


def json_domain_error_handler(error: IAMException, status_code: int):
    error_message = ErrorModel(code=error.code, message=str(error)).model_dump()
    return JSONResponse(status_code=status_code, content=error_message)


def register_error_handler(app: FastAPI) -> None:
    @app.exception_handler(IAMException)
    def handle_iam_exception(request: Request, error: IAMException):
        mapper = [
            (ForbiddenError, HTTPStatus.FORBIDDEN),
            (NotFoundError, HTTPStatus.NOT_FOUND),
            (AlreadyExistsError, HTTPStatus.CONFLICT),
            (IAMException, HTTPStatus.BAD_REQUEST),
        ]

        for error_type, status_code in mapper:
            if issubclass(type(error), error_type):
                return json_domain_error_handler(error, status_code)

    @app.exception_handler(JSONDecodeError)
    def handle_json_decode_exception(request: Request, error: JSONDecodeError):
        message = str(jsonable_encoder(error.msg))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorModel(code="json_decode_error", message=message).model_dump(),
        )

    @app.exception_handler(ValidationError)
    def handle_validation_error(request: Request, error: ValidationError):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=ErrorModel(code="bad_request", message=str(error)).model_dump(),
        )

    @app.exception_handler(DepsAuthError)
    def handle_auth_errors(request: Request, error: DepsAuthError):
        logger.error(f"Internal error {error}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorModel(code="unauthorized", message=str(error)).model_dump(),
        )

    @app.exception_handler(Exception)
    def handle_all_errors(request: Request, error: Exception):
        logger.error(f"Internal error {error}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorModel(code="internal_error", message="Something went wrong.").model_dump(),
        )
