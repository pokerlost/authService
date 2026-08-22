"""Request validation error to HTTP response mapping."""

from __future__ import annotations

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def handle_validation_error(_request: Request, exception: Exception) -> JSONResponse:
    """Return a stable validation failure without echoing submitted values."""
    if not isinstance(exception, RequestValidationError):
        raise TypeError("Unexpected exception registered as RequestValidationError")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "ok": False,
            "result": None,
            "error": "AUTH_VALIDATION_ERROR",
            "errorMessage": "Request validation failed",
        },
    )
