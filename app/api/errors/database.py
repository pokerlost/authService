"""Database error to HTTP response mapping."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from api.types import get_request_context


class DatabaseUnavailableError(Exception):
    """Required database connectivity is unavailable."""


async def handle_database_unavailable(request: Request, exception: Exception) -> JSONResponse:
    """Return the readiness-specific unavailable response."""
    if not isinstance(exception, DatabaseUnavailableError):
        raise TypeError("Unexpected exception registered as DatabaseUnavailableError")
    context = get_request_context(request)
    logfire.warn(
        "PostgreSQL readiness probe failed",
        request_id=str(context.request_id),
        correlation_id=context.correlation_id,
        _exc_info=exception,
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "ok": False,
            "result": None,
            "error": "AUTH_DATABASE_UNAVAILABLE",
            "errorMessage": "Required database is unavailable",
            "requestId": str(context.request_id),
        },
    )


async def handle_database_error(request: Request, exception: Exception) -> JSONResponse:
    """Sanitize an unexpected SQLAlchemy failure."""
    if not isinstance(exception, SQLAlchemyError):
        raise TypeError("Unexpected exception registered as SQLAlchemyError")
    context = get_request_context(request)
    logfire.error(
        "Database operation failed",
        request_id=str(context.request_id),
        correlation_id=context.correlation_id,
        _exc_info=exception,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "ok": False,
            "result": None,
            "error": "AUTH_DATABASE_ERROR",
            "errorMessage": "Database operation failed",
            "requestId": str(context.request_id),
        },
    )
