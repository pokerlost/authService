"""Body-only Pokerlost service-token operation."""

from __future__ import annotations

import re
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import SecretStr
from pypokerlost.types import (
    GetTokenRequest,
    PokerlostRequest,
    PokerlostResponse,
    PokerlostToken,
)

from api.dependencies import IssueClientCredentialsTokenHandlerDep
from application.oauth2 import GetTokenError, GetTokenErrorCode
from application.oauth2.issue_client_credentials_token import (
    IssueClientCredentialsTokenCommand,
)
from domain.resource_indicator import ResourceIndicator

_AUDIENCE_PATTERN = re.compile(r"^[a-z][A-Za-z0-9]*$")


def create_get_token_router() -> APIRouter:
    """Create the public body-only service-token router."""
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
    ) -> PokerlostResponse[PokerlostToken]:
        """Validate the body protocol and issue one exact service token."""
        payload = request.payload
        result = await handler(
            IssueClientCredentialsTokenCommand(
                client_id=_parse_client_id(payload.client_id),
                client_secret=SecretStr(payload.client_secret),
                requested_scopes=payload.scopes,
                resource=_resource_for_audience(payload.audience),
            ),
        )
        return PokerlostResponse[PokerlostToken](
            ok=True,
            result=PokerlostToken(
                access_token=result.access_token.get_secret_value(),
                refresh_token=None,
                expires_in=result.expires_in,
                scopes=result.scopes,
                audience=payload.audience,
            ),
        )

    return router


def _parse_client_id(value: str) -> UUID:
    """Parse one canonical UUID without retaining rejected credential input."""
    try:
        client_id = UUID(value)
    except ValueError:
        raise GetTokenError(GetTokenErrorCode.INVALID_CLIENT) from None
    if str(client_id) != value:
        raise GetTokenError(GetTokenErrorCode.INVALID_CLIENT)
    return client_id


def _resource_for_audience(audience: str) -> ResourceIndicator:
    """Map the public logical audience to the persisted internal resource value."""
    if _AUDIENCE_PATTERN.fullmatch(audience) is None:
        raise GetTokenError(GetTokenErrorCode.INVALID_TARGET)
    return ResourceIndicator.parse(f"urn:pokerlost:service:{audience}")
