"""Unexpected exception to HTTP response mapping."""

from __future__ import annotations

import logfire
from fastapi import Request, status
from fastapi.responses import JSONResponse

from api.request_context import request_id_from_state
from application.oauth2 import GetTokenErrorCode
from service import SERVICE_ERROR_PREFIX

from .get_token import get_token_error_response, is_get_token_request
from .response import error_response


async def handle_unexpected_error(request: Request, exception: Exception) -> JSONResponse:
    """Record an unexpected exception and return a safe public failure."""
    request_id = request_id_from_state(request)
    logfire.error(
        "Unhandled application error",
        request_id=request_id,
        _exc_info=exception,
    )
    if is_get_token_request(request):
        return get_token_error_response(GetTokenErrorCode.SERVER_ERROR)
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error=f"{SERVICE_ERROR_PREFIX}_INTERNAL_ERROR",
        error_message="Internal server error",
    )
