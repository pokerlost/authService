"""Authenticated password change RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import ChangePasswordRequest
from api.schemas.responses import ApplicationResponse
from api.types import HandlerResult
from application.accounts import ChangePasswordCommand
from application.audit import AuditContext

from .dependencies import ChangePasswordHandlerDep, ChangePasswordPrincipalDep

router = APIRouter()


@router.post(
    path=".changePassword",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Change current password",
    description="Verify and replace the authenticated human password, revoking all sessions.",
    operation_id="authService.account.changePassword",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse},
    },
)
async def change_password(
    request: Request,
    body: ChangePasswordRequest,
    principal: ChangePasswordPrincipalDep,
    handler: ChangePasswordHandlerDep,
) -> HandlerResult:
    """Replace the current credential and invalidate every issued refresh family."""
    await handler.execute(
        ChangePasswordCommand(
            current_password=body.current_password,
            new_password=body.new_password,
            audit_context=AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.account.changePassword",
                actor_principal_id=principal.principal_id,
                actor_role=principal.role,
            ),
        )
    )
    return {
        "ok": True,
        "result": None,
    }
