"""OpenAPI registry structured-value facade."""

from __future__ import annotations

from domain.openapi_registry import NormalizedAPIOperation, NormalizedAuthorizationPolicy

from .authorization_manifest import AuthorizationManifest
from .changed_operation import ChangedAPIOperation
from .contract_analysis import OpenAPIContractAnalysis
from .contract_detail import OpenAPIContractDetail
from .contract_diff import OpenAPIContractDiff
from .contract_summary import OpenAPIContractSummary
from .contracts_page import OpenAPIContractsPage
from .registered_contract import RegisteredOpenAPIContract
from .registered_service_summary import RegisteredServiceSummary
from .registered_services_page import RegisteredServicesPage
from .validation_issue import OpenAPIValidationIssue, OpenAPIValidationIssueCode
from .validation_result import OpenAPIContractValidationResult

__all__ = (
    "AuthorizationManifest",
    "ChangedAPIOperation",
    "NormalizedAPIOperation",
    "NormalizedAuthorizationPolicy",
    "OpenAPIContractAnalysis",
    "OpenAPIContractDetail",
    "OpenAPIContractDiff",
    "OpenAPIContractSummary",
    "OpenAPIContractValidationResult",
    "OpenAPIContractsPage",
    "OpenAPIValidationIssue",
    "OpenAPIValidationIssueCode",
    "RegisteredOpenAPIContract",
    "RegisteredServiceSummary",
    "RegisteredServicesPage",
)
