"""Master registered-service detail RPC."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.requests import RegisteredServiceRequest
from api.schemas.responses import ApplicationResponse, RegisteredServiceResponse
from api.types import HandlerResult
from application.openapi_registry import GetRegisteredServiceQuery

from .openapi_registry_dependencies import GetRegisteredServiceHandlerDep
from .security_dependencies import GetRegisteredServicePrincipalDep

router = APIRouter()


@router.post(
    path=".getRegisteredService",
    response_model=ApplicationResponse[RegisteredServiceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get registered service",
    description="Return one exact registered platform identity without implementation metadata.",
    operation_id="authService.master.getRegisteredService",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[RegisteredServiceResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[RegisteredServiceResponse]},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse[RegisteredServiceResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[RegisteredServiceResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[RegisteredServiceResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ApplicationResponse[RegisteredServiceResponse]
        },
    },
)
async def get_registered_service(
    request: RegisteredServiceRequest,
    _principal: GetRegisteredServicePrincipalDep,
    handler: GetRegisteredServiceHandlerDep,
) -> HandlerResult:
    """Resolve one case-sensitive platform service ID."""
    result = await handler.execute(GetRegisteredServiceQuery(service_id=request.service_id))
    return {
        "ok": True,
        "result": result,
    }
