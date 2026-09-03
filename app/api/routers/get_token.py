"""Public Pokerlost service-token operation."""

from __future__ import annotations

from fastapi import APIRouter, status
from pypokerlost.types import (
    GetTokenRequest,
    PokerlostRequest,
    PokerlostResponse,
    PokerlostToken,
)

from api.dependencies import IssueClientCredentialsTokenHandlerDep
from application.oauth2.issue_client_credentials_token import (
    IssueClientCredentialsTokenCommand,
)

router = APIRouter(tags=["tokens"])


@router.post(
    path="/getToken",
    operation_id="getToken",
    response_model=PokerlostResponse[PokerlostToken],
    status_code=status.HTTP_200_OK,
    summary="Get a service access token",
    description=(
        "Exchange service client credentials and exact grants from the JSON payload "
        "for one short-lived access token."
    ),
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": PokerlostResponse[None]},
        status.HTTP_401_UNAUTHORIZED: {"model": PokerlostResponse[None]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": PokerlostResponse[None]},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": PokerlostResponse[None]},
        "4XX": {"model": PokerlostResponse[None]},
    },
)
async def get_token(
    request: PokerlostRequest[GetTokenRequest],
    handler: IssueClientCredentialsTokenHandlerDep,
) -> dict[str, object]:
    """Issue one exact service token from validated wire input."""
    payload = request.payload
    result = await handler(
        IssueClientCredentialsTokenCommand(
            client_id=payload.client_id,
            client_secret=payload.client_secret,
            requested_scopes=payload.scopes,
            audience=payload.audience,
        ),
    )
    return {
        "ok": True,
        "result": {
            "access_token": result.access_token.get_secret_value(),
            "refresh_token": None,
            "expires_in": result.expires_in,
            "scopes": result.scopes,
            "audience": result.audience,
        },
    }
