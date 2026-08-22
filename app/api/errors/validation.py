"""Request validation error to HTTP response mapping."""

from __future__ import annotations

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.types import get_request_context


async def handle_validation_error(request: Request, exception: Exception) -> JSONResponse:
    """Return a stable validation failure without echoing submitted values."""
    if not isinstance(exception, RequestValidationError):
        raise TypeError("Unexpected exception registered as RequestValidationError")
    context = get_request_context(request)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "ok": False,
            "result": None,
            "error": "AUTH_VALIDATION_ERROR",
            "errorMessage": "Request validation failed",
            "requestId": str(context.request_id),
        },
    )
