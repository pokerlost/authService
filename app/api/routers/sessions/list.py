"""Authenticated owned-session list RPC."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.responses import ApplicationResponse, SessionsListResponse
from api.types import HandlerResult
from application.sessions import ListSessionsQuery

from .dependencies import ListSessionsHandlerDep, ListSessionsPrincipalDep

router = APIRouter()


@router.get(
    path=".list",
    response_model=ApplicationResponse[SessionsListResponse],
    status_code=status.HTTP_200_OK,
    summary="List owned human sessions",
    description="Return only sessions owned by the authenticated principal, newest first.",
    operation_id="authService.sessions.list",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[SessionsListResponse]},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[SessionsListResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse[SessionsListResponse]},
    },
)
async def list_sessions(
    principal: ListSessionsPrincipalDep,
    handler: ListSessionsHandlerDep,
) -> HandlerResult:
    """List safe session state within the authenticated ownership boundary."""
    result = await handler.execute(
        ListSessionsQuery(
            principal_id=principal.principal_id,
            current_session_id=principal.session_id,
        ),
    )
    return {
        "ok": True,
        "result": {
            "sessions": [
                {
                    "id": session.id,
                    "status": session.status,
                    "created_at": session.created_at,
                    "last_refreshed_at": session.last_refreshed_at,
                    "idle_expires_at": session.idle_expires_at,
                    "absolute_expires_at": session.absolute_expires_at,
                    "revoked_at": session.revoked_at,
                    "current": session.current,
                }
                for session in result.sessions
            ],
        },
    }
