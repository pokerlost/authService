"""Application error to HTTP response mapping."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.request_context import get_correlation_id, get_request_id
from application.errors import (
    ApplicationError,
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    InsufficientScopeError,
    InvalidAccessToken,
    InvalidOperationError,
    NotFoundError,
    RateLimitedError,
)
from application.errors import (
    IntegrityError as ApplicationIntegrityError,
)


async def handle_application_error(request: Request, exception: Exception) -> JSONResponse:
    """Map a semantic application failure without exposing internal state."""
    if not isinstance(exception, ApplicationError):
        raise TypeError("Unexpected exception registered as ApplicationError")
    if isinstance(exception, RateLimitedError):
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(exception, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exception, ForbiddenError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exception, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exception, ConflictError):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exception, InvalidOperationError):
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    elif isinstance(exception, ApplicationIntegrityError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        logfire.error(
            "Application operation failed",
            request_id=get_request_id(request),
            correlation_id=get_correlation_id(request),
            _exc_info=exception,
        )
    headers: dict[str, str] | None = None
    if isinstance(exception, InvalidAccessToken):
        headers = {"WWW-Authenticate": "Bearer"}
    elif isinstance(exception, InsufficientScopeError):
        headers = {"WWW-Authenticate": 'Bearer error="insufficient_scope"'}
    return JSONResponse(
        status_code=status_code,
        headers=headers,
        content={
            "ok": False,
            "result": None,
            "error": exception.error_code,
            "errorMessage": exception.public_message,
        },
    )
