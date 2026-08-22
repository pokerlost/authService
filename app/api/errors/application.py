"""Application error to HTTP response mapping."""

from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.types import get_request_context
from application.errors import ApplicationError


async def handle_application_error(request: Request, exception: Exception) -> JSONResponse:
    """Map a typed application failure without exposing internal state."""
    if not isinstance(exception, ApplicationError):
        raise TypeError("Unexpected exception registered as ApplicationError")
    context = get_request_context(request)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "ok": False,
            "result": None,
            "error": exception.error_code,
            "errorMessage": exception.public_message,
            "requestId": str(context.request_id),
        },
    )
