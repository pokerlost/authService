"""Authenticated all-session logout RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.sessions import RevokeAllSessionsCommand

from .dependencies import LogoutAllPrincipalDep, RevokeAllSessionsHandlerDep

router = APIRouter()


@router.post(
    path=".logoutAll",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Log out all owned human sessions",
    description="Revoke every active session and refresh-token family owned by the principal.",
    operation_id="authService.auth.logoutAll",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def logout_all(
    request: Request,
    principal: LogoutAllPrincipalDep,
    handler: RevokeAllSessionsHandlerDep,
) -> HandlerResult:
    """Revoke all sessions using only the authenticated principal identity."""
    await handler.execute(
        RevokeAllSessionsCommand(
            principal_id=principal.principal_id,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.auth.logoutAll",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": None,
    }
