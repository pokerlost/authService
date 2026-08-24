"""Master direct role scope grant RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import RoleScopeRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.scope_grants import GrantRoleScopeCommand

from .scope_grant_dependencies import GrantRoleScopeHandlerDep
from .security_dependencies import GrantRoleScopePrincipalDep

router = APIRouter()


@router.post(
    path=".grantRoleScope",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Grant role scope",
    description="Grant one active canonical operation scope to one explicit human role.",
    operation_id="authService.master.grantRoleScope",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def grant_role_scope(
    request: Request,
    body: RoleScopeRequest,
    principal: GrantRoleScopePrincipalDep,
    handler: GrantRoleScopeHandlerDep,
) -> HandlerResult:
    """Create one direct role grant without inheritance or wildcard semantics."""
    await handler.execute(
        GrantRoleScopeCommand(
            role=body.role,
            scope=body.scope,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.master.grantRoleScope",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": None,
    }
