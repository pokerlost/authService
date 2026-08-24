"""Unexpected exception to HTTP response mapping."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.request_context import get_correlation_id, get_request_id


async def handle_unexpected_error(request: Request, exception: Exception) -> JSONResponse:
    """Record an unexpected exception and return a safe public failure."""
    request_id = get_request_id(request)
    correlation_id = get_correlation_id(request)
    logfire.error(
        "Unhandled application error",
        request_id=request_id,
        correlation_id=correlation_id,
        _exc_info=exception,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "ok": False,
            "result": None,
            "error": "AUTH_INTERNAL_ERROR",
            "errorMessage": "Internal server error",
        },
    )
