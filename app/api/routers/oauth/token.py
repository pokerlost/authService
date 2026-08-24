"""Unified PokerLost OAuth2 token RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from api.request_context import get_correlation_id, get_request_id
from api.schemas.responses import ApplicationResponse, OAuthTokenResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.errors import (
    InvalidOAuthClient,
    InvalidOAuthGrant,
    InvalidOAuthScope,
    RateLimitedError,
    UnsupportedOAuthGrantType,
)
from application.oauth import OAuthTokenCommand
from domain.enums import OAuthTokenStatus

from .dependencies import (
    OAuthClientAuthenticationDep,
    OAuthTokenFormDep,
    OAuthTokenHandlerDep,
)

router = APIRouter()

_ERRORS = {
    OAuthTokenStatus.INVALID_GRANT: (
        status.HTTP_400_BAD_REQUEST,
        InvalidOAuthGrant.error_code,
        InvalidOAuthGrant.public_message,
    ),
    OAuthTokenStatus.INVALID_CLIENT: (
        status.HTTP_401_UNAUTHORIZED,
        InvalidOAuthClient.error_code,
        InvalidOAuthClient.public_message,
    ),
    OAuthTokenStatus.INVALID_SCOPE: (
        status.HTTP_400_BAD_REQUEST,
        InvalidOAuthScope.error_code,
        InvalidOAuthScope.public_message,
    ),
    OAuthTokenStatus.UNSUPPORTED_GRANT_TYPE: (
        status.HTTP_400_BAD_REQUEST,
        UnsupportedOAuthGrantType.error_code,
        UnsupportedOAuthGrantType.public_message,
    ),
    OAuthTokenStatus.RATE_LIMITED: (
        status.HTTP_429_TOO_MANY_REQUESTS,
        RateLimitedError.error_code,
        RateLimitedError.public_message,
    ),
}


@router.post(
    path=".token",
    response_model=ApplicationResponse[OAuthTokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Issue an OAuth2 access token",
    description=(
        "Process password, refresh_token, or client_credentials grant semantics using form data."
    ),
    operation_id="authService.oauth.token",
    openapi_extra={"security": []},
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ApplicationResponse[OAuthTokenResponse]},
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[OAuthTokenResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse[OAuthTokenResponse]},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": ApplicationResponse[OAuthTokenResponse]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse[OAuthTokenResponse]},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse[OAuthTokenResponse]},
    },
)
async def issue_oauth_token(
    request: Request,
    form: OAuthTokenFormDep,
    client_authentication: OAuthClientAuthenticationDep,
    handler: OAuthTokenHandlerDep,
) -> HandlerResult | JSONResponse:
    """Return a wrapped token or a wrapped stable OAuth2 grant error."""
    result = await handler.execute(
        OAuthTokenCommand(
            grant_type=form.grant_type,
            username=form.username,
            password=form.password,
            refresh_token=form.refresh_token,
            scope=form.scope,
            resource=form.resource,
            client_id=(
                client_authentication.username if client_authentication is not None else None
            ),
            client_secret=(
                client_authentication.password if client_authentication is not None else None
            ),
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.oauth.token",
            ),
        )
    )
    if result.status is not OAuthTokenStatus.SUCCESS:
        status_code, error, message = _ERRORS[result.status]
        headers = (
            {"WWW-Authenticate": "Basic"}
            if result.status is OAuthTokenStatus.INVALID_CLIENT
            else None
        )
        return JSONResponse(
            status_code=status_code,
            headers=headers,
            content={
                "ok": False,
                "result": None,
                "error": error,
                "errorMessage": message,
            },
        )
    if result.access_token is None or result.expires_in is None:
        raise RuntimeError("Successful OAuth2 result is incomplete")
    return {
        "ok": True,
        "result": {
            "access_token": result.access_token,
            "token_type": "Bearer",
            "expires_in": result.expires_in,
            "scope": " ".join(sorted(result.scopes)),
            "refresh_token": result.refresh_token,
        },
    }
