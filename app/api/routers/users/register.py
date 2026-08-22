"""Public ordinary-user registration endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.schemas.orm import PrincipalSchema
from api.schemas.requests import RegisterUserRequest
from api.schemas.responses import ApplicationResponse
from application.users import RegisterUserHandler

from .dependencies import provide_register_user

router = APIRouter()


@router.post(
    path=".register",
    response_model=ApplicationResponse[PrincipalSchema],
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    summary="Register an ordinary PokerLost user",
    description=(
        "Create one active human principal with the direct user role and Argon2id credential."
    ),
    operation_id="authService.users.register",
    openapi_extra={"x-pokerlost-authz": {"public": True}},
    responses={
        status.HTTP_409_CONFLICT: {
            "model": ApplicationResponse[None],
            "description": "The normalized email is already registered.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[None],
            "description": "The request payload is invalid.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[None],
            "description": "PostgreSQL is unavailable.",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[None],
            "description": "Sanitized internal failure.",
        },
    },
    tags=["users"],
)
async def register_user(
    request: RegisterUserRequest,
    handler: Annotated[RegisterUserHandler, Depends(provide_register_user)],
) -> dict[str, object]:
    """Register an ordinary user inside one request-owned transaction."""
    principal = await handler.execute(request.to_command())
    return {"ok": True, "result": principal}
