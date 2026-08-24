"""OpenAPI registry response facade."""

from __future__ import annotations

from .api_operation_response import ApiOperationResponse
from .authorization_manifest_response import AuthorizationManifestResponse
from .authorization_response import (
    AuthorizationResponse,
    OAuth2AuthorizationResponse,
    PublicAuthorizationResponse,
)
from .contract_diff_response import ChangedApiOperationResponse, ContractDiffResponse
from .openapi_contract_response import OpenApiContractResponse
from .openapi_contract_summary_response import OpenApiContractSummaryResponse
from .openapi_contract_validation_response import ValidationIssueResponse, ValidationResponse
from .openapi_contracts_page_response import OpenApiContractsPageResponse
from .registered_openapi_contract_response import RegisteredOpenApiContractResponse
from .registered_service_response import RegisteredServiceResponse
from .registered_services_page_response import RegisteredServicesPageResponse

__all__ = (
    "ApiOperationResponse",
    "AuthorizationManifestResponse",
    "AuthorizationResponse",
    "ChangedApiOperationResponse",
    "ContractDiffResponse",
    "OAuth2AuthorizationResponse",
    "OpenApiContractResponse",
    "OpenApiContractSummaryResponse",
    "OpenApiContractsPageResponse",
    "PublicAuthorizationResponse",
    "RegisteredOpenApiContractResponse",
    "RegisteredServiceResponse",
    "RegisteredServicesPageResponse",
    "ValidationIssueResponse",
    "ValidationResponse",
)
