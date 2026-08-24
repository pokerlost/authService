"""Master durable security audit list RPC."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.requests import ListAuditEventsRequest
from api.schemas.responses import ApplicationResponse, AuditEventsPageResponse
from api.types import HandlerResult

from .audit_dependencies import ListAuditEventsHandlerDep
from .security_dependencies import ListAuditEventsPrincipalDep

router = APIRouter()


@router.post(
    path=".listAuditEvents",
    response_model=ApplicationResponse[AuditEventsPageResponse],
    status_code=status.HTTP_200_OK,
    summary="List security audit events",
    description="Return a bounded newest-first keyset page of durable security audit events.",
    operation_id="authService.master.listAuditEvents",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[AuditEventsPageResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[AuditEventsPageResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[AuditEventsPageResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[AuditEventsPageResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[AuditEventsPageResponse]
        },
    },
)
async def list_audit_events(
    request: ListAuditEventsRequest,
    _principal: ListAuditEventsPrincipalDep,
    handler: ListAuditEventsHandlerDep,
) -> HandlerResult:
    """Return only safe append-only audit fields and bounded metadata."""
    page = await handler.execute(request.to_query())
    return {
        "ok": True,
        "result": {
            "items": [
                {
                    "id": event.id,
                    "occurred_at": event.occurred_at,
                    "event_type": event.event_type,
                    "result": event.result,
                    "actor_principal_id": event.actor_principal_id,
                    "actor_role": event.actor_role,
                    "target_type": event.target_type,
                    "target_id": event.target_id,
                    "request_id": event.request_id,
                    "correlation_id": event.correlation_id,
                    "api_operation_id": event.api_operation_id,
                    "metadata": event.event_metadata,
                }
                for event in page.items
            ],
            "next_before_occurred_at": page.next_before_occurred_at,
            "next_before_id": page.next_before_id,
        },
    }
