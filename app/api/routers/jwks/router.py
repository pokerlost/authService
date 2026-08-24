"""JWKS endpoint for public signing key publication."""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from api.dependencies import SettingsDep
from api.openapi import OpenAPITag
from api.schemas.responses import ApplicationResponse, JwksResponse
from api.types import HandlerResult

from .dependencies import SigningKeyProviderDep

router = APIRouter(tags=[OpenAPITag.JWKS])


@router.get(
    path="/jwks.get",
    response_model=ApplicationResponse[JwksResponse],
    status_code=status.HTTP_200_OK,
    summary="Get JWT signing keys",
    description=(
        "Return the currently active and retained public keys used for RS256 access token signing."
    ),
    operation_id="authService.jwks.get",
    openapi_extra={"security": []},
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[JwksResponse],
        },
    },
)
async def get_jwks(
    response: Response,
    settings: SettingsDep,
    signing_key_provider: SigningKeyProviderDep,
) -> HandlerResult:
    """Expose public signing keys for token validation."""
    response.headers["Cache-Control"] = f"public, max-age={settings.jwt.jwks_cache_ttl_seconds}"
    return {
        "ok": True,
        "result": signing_key_provider.get_jwks_payload(),
    }
