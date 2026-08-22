"""JWKS endpoint for public signing key publication."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from api.dependencies import get_application_resources, get_settings
from api.resources import ApplicationResources
from api.schemas.responses import JwksSchema
from application.security import SigningKeyProvider
from configuration import Settings

router = APIRouter()


def provide_signing_key_provider(
    resources: Annotated[ApplicationResources, Depends(get_application_resources)],
) -> SigningKeyProvider:
    """Expose signing keys for JWKS serialization."""
    return resources.signing_key_provider


@router.get(
    path="/.well-known/jwks.json",
    response_model=JwksSchema,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Get JWT signing keys",
    description=(
        "Return the currently active and retained public keys used for RS256 access token signing."
    ),
    operation_id="authService.jwks.get",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Signing key configuration is currently unavailable.",
        },
    },
    openapi_extra={
        "x-pokerlost-authz": {
            "public": True,
        },
    },
    tags=["jwks"],
)
async def get_jwks(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
    signing_key_provider: Annotated[
        SigningKeyProvider,
        Depends(provide_signing_key_provider),
    ],
) -> dict[str, list[dict[str, str]]]:
    """Expose public signing keys for token validation."""
    response.headers["Cache-Control"] = f"public, max-age={settings.jwt.jwks_cache_ttl_seconds}"
    return signing_key_provider.get_jwks_payload()
