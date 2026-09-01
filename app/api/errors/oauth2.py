"""OAuth2 token endpoint error detection and envelope serialization."""

from __future__ import annotations

from typing import Final

from fastapi import Request, status
from fastapi.responses import JSONResponse

from application.oauth2 import OAuth2ErrorCode, OAuth2TokenError
from service import SERVICE_ERROR_PREFIX

from .response import error_response

NO_STORE_HEADERS: Final[dict[str, str]] = {
    "Cache-Control": "no-store",
    "Pragma": "no-cache",
}

_ERROR_MESSAGES: Final[dict[OAuth2ErrorCode, str]] = {
    OAuth2ErrorCode.INVALID_REQUEST: "The request is invalid.",
    OAuth2ErrorCode.UNSUPPORTED_GRANT_TYPE: ("The authorization grant type is not supported."),
    OAuth2ErrorCode.INVALID_CLIENT: "Client authentication failed.",
    OAuth2ErrorCode.UNAUTHORIZED_CLIENT: (
        "The authenticated client is not authorized to use this grant type."
    ),
    OAuth2ErrorCode.INVALID_SCOPE: "The requested scope is invalid.",
    OAuth2ErrorCode.INVALID_TARGET: "The requested resource is invalid.",
    OAuth2ErrorCode.TEMPORARILY_UNAVAILABLE: (
        "The authorization server is temporarily unavailable."
    ),
    OAuth2ErrorCode.SERVER_ERROR: ("The authorization server encountered an unexpected condition."),
}


def is_oauth_token_request(request: Request) -> bool:
    """Return whether the request targets the exact OAuth2 token path."""
    from api.routers.oauth_token.router import OPERATION

    return request.url.path == f"/{OPERATION}"


def oauth2_error_response(error: OAuth2ErrorCode) -> JSONResponse:
    """Serialize one stable application failure with mandatory cache prevention."""
    if error is OAuth2ErrorCode.INVALID_CLIENT:
        status_code = status.HTTP_401_UNAUTHORIZED
    elif error is OAuth2ErrorCode.TEMPORARILY_UNAVAILABLE:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif error is OAuth2ErrorCode.SERVER_ERROR:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    headers = dict(NO_STORE_HEADERS)
    if error is OAuth2ErrorCode.INVALID_CLIENT:
        headers["WWW-Authenticate"] = "Basic"
    return error_response(
        status_code=status_code,
        error=f"{SERVICE_ERROR_PREFIX}_{error.value.upper()}",
        error_message=_ERROR_MESSAGES[error],
        headers=headers,
    )


async def handle_oauth2_token_error(
    _request: Request,
    exception: Exception,
) -> JSONResponse:
    """Map one expected token failure to the universal application envelope."""
    if not isinstance(exception, OAuth2TokenError):
        raise TypeError("Unexpected exception registered as OAuth2TokenError")
    return oauth2_error_response(exception.error)
