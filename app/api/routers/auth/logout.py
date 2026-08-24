"""Authenticated current-session logout RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.audit import AuditContext
from application.sessions import RevokeCurrentSessionCommand

from .dependencies import LogoutPrincipalDep, RevokeCurrentSessionHandlerDep

router = APIRouter()


@router.post(
    path=".logout",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Log out current human session",
    description="Revoke the authenticated session and its active refresh-token family.",
    operation_id="authService.auth.logout",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def logout(
    request: Request,
    principal: LogoutPrincipalDep,
    handler: RevokeCurrentSessionHandlerDep,
) -> HandlerResult:
    """Revoke the current session derived only from trusted access claims."""
    await handler.execute(
        RevokeCurrentSessionCommand(
            principal_id=principal.principal_id,
            session_id=principal.session_id,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.auth.logout",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        ),
    )
    return {
        "ok": True,
        "result": None,
    }
