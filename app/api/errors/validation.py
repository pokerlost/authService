"""Request validation error to HTTP response mapping."""

from __future__ import annotations

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from application.oauth2 import OAuth2ErrorCode
from service import SERVICE_ERROR_PREFIX

from .oauth2 import is_oauth_token_request, oauth2_error_response
from .response import error_response


async def handle_validation_error(request: Request, exception: Exception) -> JSONResponse:
    """Return a stable validation failure without echoing submitted values."""
    if not isinstance(exception, RequestValidationError):
        raise TypeError("Unexpected exception registered as RequestValidationError")
    if is_oauth_token_request(request):
        content_type = request.headers.get("content-type", "").partition(";")[0].strip().lower()
        if content_type != "application/x-www-form-urlencoded":
            return oauth2_error_response(OAuth2ErrorCode.INVALID_REQUEST)
        missing_resource = any(
            error.get("type") == "missing" and tuple(error.get("loc", ()))[-1:] == ("resource",)
            for error in exception.errors()
        )
        return oauth2_error_response(
            OAuth2ErrorCode.INVALID_TARGET if missing_resource else OAuth2ErrorCode.INVALID_REQUEST
        )
    return error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error=f"{SERVICE_ERROR_PREFIX}_VALIDATION_ERROR",
        error_message="Request validation failed",
    )
