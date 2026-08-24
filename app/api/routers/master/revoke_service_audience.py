"""Master AUTO audience revocation RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import ServiceAudienceRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.service_authentication import RevokeServiceAudienceCommand

from .security_dependencies import RevokeServiceAudiencePrincipalDep
from .service_authentication_dependencies import RevokeServiceAudienceHandlerDep

router = APIRouter()


@router.post(
    path=".revokeServiceAudience",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke service audience",
    description="Idempotently remove one exact AUTO source-to-target audience grant.",
    operation_id="authService.master.revokeServiceAudience",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def revoke_service_audience(
    request: Request,
    body: ServiceAudienceRequest,
    principal: RevokeServiceAudiencePrincipalDep,
    handler: RevokeServiceAudienceHandlerDep,
) -> HandlerResult:
    """Reuse the accepted exact audience revocation handler."""
    await handler.execute(
        RevokeServiceAudienceCommand(
            service_slug=body.service_slug,
            audience=body.audience,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.revokeServiceAudience",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": None,
    }
