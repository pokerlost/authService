"""Application error to HTTP response mapping."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.request_context import request_id_from_state
from application.errors import (
    ApplicationError,
    ConflictError,
    IntegrityError,
    InvalidOperationError,
    NotFoundError,
)
from application.oauth2 import GetTokenErrorCode

from .get_token import get_token_error_response, is_get_token_request
from .response import error_response


async def handle_application_error(request: Request, exception: Exception) -> JSONResponse:
    """Map a semantic application failure without exposing internal state."""
    if not isinstance(exception, ApplicationError):
        raise TypeError("Unexpected exception registered as ApplicationError")
    if is_get_token_request(request):
        logfire.error(
            "getToken application operation failed",
            request_id=request_id_from_state(request),
            _exc_info=exception,
        )
        return get_token_error_response(GetTokenErrorCode.SERVER_ERROR)
    if isinstance(exception, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exception, ConflictError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exception, InvalidOperationError):
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    elif isinstance(exception, IntegrityError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        logfire.error(
            "Application operation failed",
            request_id=request_id_from_state(request),
            _exc_info=exception,
        )
    return error_response(
        status_code=status_code,
        error=exception.error_code,
        error_message=exception.public_message,
    )
