"""Master service scope revocation RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import ServiceScopeRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.scope_grants import RevokeServiceScopeCommand

from .scope_grant_dependencies import RevokeServiceScopeHandlerDep
from .security_dependencies import RevokeServiceScopePrincipalDep

router = APIRouter()


@router.post(
    path=".revokeServiceScope",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke service scope",
    description="Idempotently revoke one exact source, audience, and operation scope grant.",
    operation_id="authService.master.revokeServiceScope",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def revoke_service_scope(
    request: Request,
    body: ServiceScopeRequest,
    principal: RevokeServiceScopePrincipalDep,
    handler: RevokeServiceScopeHandlerDep,
) -> HandlerResult:
    """Remove a service grant without invalidating existing access JWTs."""
    await handler.execute(
        RevokeServiceScopeCommand(
            service_slug=body.service_slug,
            audience=body.audience,
            scope=body.scope,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.revokeServiceScope",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": None,
    }
