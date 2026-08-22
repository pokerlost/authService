"""Unexpected exception to HTTP response mapping."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.request_context import CORRELATION_ID_HEADER, REQUEST_ID_HEADER
from api.types import get_request_context


async def handle_unexpected_error(request: Request, exception: Exception) -> JSONResponse:
    """Record an unexpected exception and return a safe public failure."""
    context = get_request_context(request)
    logfire.error(
        "Unhandled application error",
        request_id=str(context.request_id),
        correlation_id=context.correlation_id,
        _exc_info=exception,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers={
            REQUEST_ID_HEADER: str(context.request_id),
            CORRELATION_ID_HEADER: context.correlation_id,
        },
        content={
            "ok": False,
            "result": None,
            "error": "AUTH_INTERNAL_ERROR",
            "errorMessage": "Internal server error",
            "requestId": str(context.request_id),
        },
    )
