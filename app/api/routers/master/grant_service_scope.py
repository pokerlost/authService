"""Master service scope grant RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import ServiceScopeRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.scope_grants import GrantServiceScopeCommand

from .scope_grant_dependencies import GrantServiceScopeHandlerDep
from .security_dependencies import GrantServiceScopePrincipalDep

router = APIRouter()


@router.post(
    path=".grantServiceScope",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Grant service scope",
    description="Grant an active resource-owned scope after an exact audience grant.",
    operation_id="authService.master.grantServiceScope",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def grant_service_scope(
    request: Request,
    body: ServiceScopeRequest,
    principal: GrantServiceScopePrincipalDep,
    handler: GrantServiceScopeHandlerDep,
) -> HandlerResult:
    """Create one exact source, audience, and operation scope grant."""
    await handler.execute(
        GrantServiceScopeCommand(
            service_slug=body.service_slug,
            audience=body.audience,
            scope=body.scope,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.grantServiceScope",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": None,
    }
