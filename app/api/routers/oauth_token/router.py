"""OAuth2 token protocol endpoint."""

from __future__ import annotations

from typing import Final

from fastapi import APIRouter, Response, status
from pypokerlost.types import APIOperation

from api.dependencies import (
    IssueClientCredentialsTokenHandlerDep,
    OAuthClientAuthentication,
    OAuthTokenProtocolInput,
)
from api.errors.oauth2 import NO_STORE_HEADERS
from api.schemas.responses import ApplicationResponse, OAuthTokenResponse
from application.oauth2.issue_client_credentials_token import (
    IssueClientCredentialsTokenCommand,
)

OPERATION: Final[APIOperation] = "oauth.token"

router = APIRouter(tags=["oauth2"])


@router.post(
    path=f"/{OPERATION}",
    operation_id=OPERATION,
    response_model=ApplicationResponse[OAuthTokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Issue a service access token",
    description=(
        "Exchange an authenticated confidential client's exact direct grants for one "
        "short-lived service access token."
    ),
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ApplicationResponse[None]},
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[None]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse[None]},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse[None]},
        "4XX": {"model": ApplicationResponse[None]},
    },
)
async def issue_oauth_token(
    response: Response,
    protocol_input: OAuthTokenProtocolInput,
    authentication: OAuthClientAuthentication,
    handler: IssueClientCredentialsTokenHandlerDep,
) -> ApplicationResponse[OAuthTokenResponse]:
    """Translate the typed form and Basic credentials into token issuance."""
    result = await handler.execute(
        IssueClientCredentialsTokenCommand(
            client_id=authentication.client_id,
            client_secret=authentication.client_secret,
            requested_scopes=protocol_input.requested_scopes,
            resource=protocol_input.resource,
        ),
    )
    response.headers.update(NO_STORE_HEADERS)
    return ApplicationResponse[OAuthTokenResponse](
        ok=True,
        result=OAuthTokenResponse(
            access_token=result.access_token.get_secret_value(),
            token_type="bearer",
            expires_in=result.expires_in,
            scope=result.scope,
        ),
    )
