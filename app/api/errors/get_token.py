"""Body-only getToken error detection and envelope serialization."""

from __future__ import annotations

from typing import Final

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pypokerlost.types import PokerlostResponse

from application.oauth2 import GetTokenError, GetTokenErrorCode
from service import SERVICE_ERROR_PREFIX

_ERROR_MESSAGES: Final[dict[GetTokenErrorCode, str]] = {
    GetTokenErrorCode.INVALID_REQUEST: "The request is invalid.",
    GetTokenErrorCode.INVALID_CLIENT: "Client authentication failed.",
    GetTokenErrorCode.UNAUTHORIZED_CLIENT: (
        "The authenticated client is not authorized to request a token."
    ),
    GetTokenErrorCode.INVALID_SCOPE: "The requested scope is invalid.",
    GetTokenErrorCode.INVALID_TARGET: "The requested audience is invalid.",
    GetTokenErrorCode.TEMPORARILY_UNAVAILABLE: "The token service is temporarily unavailable.",
    GetTokenErrorCode.SERVER_ERROR: "The token service encountered an unexpected condition.",
}


def is_get_token_request(request: Request) -> bool:
    """Return whether the request targets the exact getToken path."""
    return request.url.path == "/getToken"


def get_token_error_response(error: GetTokenErrorCode) -> JSONResponse:
    """Serialize one stable PokerlostResponse failure without transport metadata."""
    if error is GetTokenErrorCode.INVALID_CLIENT:
        status_code = status.HTTP_401_UNAUTHORIZED
    elif error is GetTokenErrorCode.TEMPORARILY_UNAVAILABLE:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif error is GetTokenErrorCode.SERVER_ERROR:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    response = PokerlostResponse[None](
        ok=False,
        error=f"{SERVICE_ERROR_PREFIX}_{error.value.upper()}",
        error_message=_ERROR_MESSAGES[error],
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(mode="json"),
    )


async def handle_get_token_error(
    _request: Request,
    exception: Exception,
) -> JSONResponse:
    """Map one expected token failure to the canonical response envelope."""
    if not isinstance(exception, GetTokenError):
        raise TypeError("Unexpected exception registered as GetTokenError")
    return get_token_error_response(exception.error)
