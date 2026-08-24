"""Authenticated owned-session revocation RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import RevokeSessionRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.audit import AuditContext

from .dependencies import RevokeSessionHandlerDep, RevokeSessionPrincipalDep

router = APIRouter()


@router.post(
    path=".revoke",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke one owned human session",
    description="Revoke one owned session and its active refresh credential without role bypass.",
    operation_id="authService.sessions.revoke",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def revoke_session(
    request: Request,
    body: RevokeSessionRequest,
    principal: RevokeSessionPrincipalDep,
    handler: RevokeSessionHandlerDep,
) -> HandlerResult:
    """Revoke an owned target without accepting caller-supplied principal identity."""
    await handler.execute(
        body.to_command(
            principal_id=principal.principal_id,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.sessions.revoke",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": None,
    }
