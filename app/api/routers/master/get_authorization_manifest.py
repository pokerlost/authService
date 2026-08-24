"""Master active authorization manifest RPC."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.requests import RegisteredServiceRequest
from api.schemas.responses import ApplicationResponse, AuthorizationManifestResponse
from api.types import HandlerResult
from application.openapi_registry import GetAuthorizationManifestQuery

from .openapi_registry_dependencies import GetAuthorizationManifestHandlerDep
from .security_dependencies import GetAuthorizationManifestPrincipalDep

router = APIRouter()


@router.post(
    path=".getAuthorizationManifest",
    response_model=ApplicationResponse[AuthorizationManifestResponse],
    status_code=status.HTTP_200_OK,
    summary="Get authorization manifest",
    description="Return the normalized explicitly active control-plane manifest for one service.",
    operation_id="authService.master.getAuthorizationManifest",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": ApplicationResponse[AuthorizationManifestResponse]
        },
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[AuthorizationManifestResponse]},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse[AuthorizationManifestResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[AuthorizationManifestResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[AuthorizationManifestResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[AuthorizationManifestResponse]
        },
    },
)
async def get_authorization_manifest(
    request: RegisteredServiceRequest,
    _principal: GetAuthorizationManifestPrincipalDep,
    handler: GetAuthorizationManifestHandlerDep,
) -> HandlerResult:
    """Return active normalized metadata, never a per-request authorization decision."""
    manifest = await handler.execute(GetAuthorizationManifestQuery(service_id=request.service_id))
    return {
        "ok": True,
        "result": {
            "service_id": manifest.service_id,
            "contract_id": manifest.contract_id,
            "contract_version": manifest.contract_version,
            "schema_hash": manifest.schema_hash,
            "operations": [operation.canonical_payload() for operation in manifest.operations],
        },
    }
