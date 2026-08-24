"""Master AUTO audience grant RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import ServiceAudienceRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.service_authentication import GrantServiceAudienceCommand

from .security_dependencies import GrantServiceAudiencePrincipalDep
from .service_authentication_dependencies import GrantServiceAudienceHandlerDep

router = APIRouter()


@router.post(
    path=".grantServiceAudience",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Grant service audience",
    description="Idempotently permit one AUTO source identity to request one target audience.",
    operation_id="authService.master.grantServiceAudience",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def grant_service_audience(
    request: Request,
    body: ServiceAudienceRequest,
    principal: GrantServiceAudiencePrincipalDep,
    handler: GrantServiceAudienceHandlerDep,
) -> HandlerResult:
    """Reuse the accepted exact source-to-target audience grant handler."""
    await handler.execute(
        GrantServiceAudienceCommand(
            service_slug=body.service_slug,
            audience=body.audience,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.grantServiceAudience",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": None,
    }
