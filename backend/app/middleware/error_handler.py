import traceback

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.services.exceptions import (
    InvalidUserDataException,
    UserAlreadyExistsException,
)

logger = get_logger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    pass

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        },
    )


async def user_already_exists_handler(
    request: Request, exc: UserAlreadyExistsException
) -> JSONResponse:
    pass

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": {
                "code": "USER_ALREADY_EXISTS",
                "message": str(exc),
                "status_code": status.HTTP_409_CONFLICT,
            }
        },
    )


async def invalid_user_data_handler(
    request: Request, exc: InvalidUserDataException
) -> JSONResponse:
    pass

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "INVALID_USER_DATA",
                "message": str(exc),
                "status_code": status.HTTP_400_BAD_REQUEST,
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    pass

    # Print complete traceback to console
    traceback.print_exc()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore
    app.add_exception_handler(UserAlreadyExistsException, user_already_exists_handler)  # type: ignore
    app.add_exception_handler(InvalidUserDataException, invalid_user_data_handler)  # type: ignore
    app.add_exception_handler(Exception, generic_exception_handler)
