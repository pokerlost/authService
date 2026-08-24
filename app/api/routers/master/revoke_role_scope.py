"""Master direct role scope revocation RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import RoleScopeRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.scope_grants import RevokeRoleScopeCommand

from .scope_grant_dependencies import RevokeRoleScopeHandlerDep
from .security_dependencies import RevokeRoleScopePrincipalDep

router = APIRouter()


@router.post(
    path=".revokeRoleScope",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke role scope",
    description="Idempotently revoke one exact direct human role scope grant.",
    operation_id="authService.master.revokeRoleScope",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def revoke_role_scope(
    request: Request,
    body: RoleScopeRequest,
    principal: RevokeRoleScopePrincipalDep,
    handler: RevokeRoleScopeHandlerDep,
) -> HandlerResult:
    """Remove a role grant while leaving access JWTs valid until expiration."""
    await handler.execute(
        RevokeRoleScopeCommand(
            role=body.role,
            scope=body.scope,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.revokeRoleScope",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": None,
    }
