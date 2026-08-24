"""Master OpenAPI contract diff RPC."""

from __future__ import annotations

from fastapi import APIRouter, status

from api.schemas.requests import OpenAPIContractRequest
from api.schemas.responses import ApplicationResponse, ContractDiffResponse
from api.types import HandlerResult
from application.openapi_registry import DiffOpenAPIContractQuery

from .openapi_registry_dependencies import DiffOpenAPIContractHandlerDep
from .security_dependencies import DiffOpenApiContractPrincipalDep

router = APIRouter()


@router.post(
    path=".diffOpenApiContract",
    response_model=ApplicationResponse[ContractDiffResponse],
    status_code=status.HTTP_200_OK,
    summary="Diff OpenAPI contract",
    description=(
        "Compare one validated candidate with the currently active contract of the same service."
    ),
    operation_id="authService.master.diffOpenApiContract",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ApplicationResponse[ContractDiffResponse]},
        status.HTTP_403_FORBIDDEN: {"model": ApplicationResponse[ContractDiffResponse]},
        status.HTTP_404_NOT_FOUND: {"model": ApplicationResponse[ContractDiffResponse]},
        status.HTTP_409_CONFLICT: {"model": ApplicationResponse[ContractDiffResponse]},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ApplicationResponse[ContractDiffResponse]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "model": ApplicationResponse[ContractDiffResponse]
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ApplicationResponse[ContractDiffResponse]},
    },
)
async def diff_openapi_contract(
    request: OpenAPIContractRequest,
    _principal: DiffOpenApiContractPrincipalDep,
    handler: DiffOpenAPIContractHandlerDep,
) -> HandlerResult:
    """Return canonical operation changes and a candidate-specific diff hash."""
    diff = await handler.execute(DiffOpenAPIContractQuery(contract_id=request.contract_id))
    return {
        "ok": True,
        "result": {
            "base_contract_id": diff.base_contract_id,
            "candidate_contract_id": diff.candidate_contract_id,
            "diff_hash": diff.diff_hash,
            "added_operations": [
                operation.canonical_payload() for operation in diff.added_operations
            ],
            "removed_operations": [
                operation.canonical_payload() for operation in diff.removed_operations
            ],
            "changed_operations": [
                {
                    "operationId": change.api_operation_id,
                    "before": change.before.canonical_payload(),
                    "after": change.after.canonical_payload(),
                    "security_change_level": change.security_change_level,
                }
                for change in diff.changed_operations
            ],
            "security_change_level": diff.security_change_level,
            "requires_security_acknowledgement": (diff.requires_security_acknowledgement),
        },
    }
