"""Public ordinary-user registration RPC."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from api.request_context import get_correlation_id, get_request_id
from api.schemas.requests import RegisterUserRequest
from api.schemas.responses import AccountResponse, ApplicationResponse
from api.types import HandlerResult
from application.audit import AuditContext

from .dependencies import RegisterUserHandlerDep

router = APIRouter()


@router.post(
    path=".register",
    response_model=ApplicationResponse[AccountResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register ordinary user",
    description="Create one active ordinary-user account with a canonical username.",
    operation_id="authService.users.register",
    openapi_extra={"security": []},
    responses={
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse[AccountResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ApplicationResponse[AccountResponse]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ApplicationResponse[AccountResponse]},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse[AccountResponse]},
    },
)
async def register_user(
    request: Request,
    body: RegisterUserRequest,
    handler: RegisterUserHandlerDep,
) -> HandlerResult:
    """Register one ordinary user without establishing a session."""
    result = await handler.execute(
        body.to_command(
            AuditContext(
                request_id=get_request_id(request),
                correlation_id=get_correlation_id(request),
                api_operation_id="authService.users.register",
            )
        )
    )
    return {
        "ok": True,
        "result": result,
    }
