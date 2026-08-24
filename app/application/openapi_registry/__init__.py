"""OpenAPI authorization registry application facade."""

from __future__ import annotations

from .activate_contract import ActivateOpenAPIContractCommand, ActivateOpenAPIContractHandler
from .contract_analyzer import OpenAPIContractAnalyzer
from .contract_diff_calculator import OpenAPIContractDiffCalculator
from .diff_contract import DiffOpenAPIContractHandler, DiffOpenAPIContractQuery
from .get_contract import GetOpenAPIContractHandler, GetOpenAPIContractQuery
from .get_manifest import GetAuthorizationManifestHandler, GetAuthorizationManifestQuery
from .get_registered_service import GetRegisteredServiceHandler, GetRegisteredServiceQuery
from .list_contracts import ListOpenAPIContractsHandler, ListOpenAPIContractsQuery
from .list_registered_services import (
    ListRegisteredServicesHandler,
    ListRegisteredServicesQuery,
)
from .register_contract import RegisterOpenAPIContractCommand, RegisterOpenAPIContractHandler
from .retire_contract import RetireOpenAPIContractCommand, RetireOpenAPIContractHandler
from .validate_contract import ValidateOpenAPIContractCommand, ValidateOpenAPIContractHandler
from .values import (
    AuthorizationManifest,
    ChangedAPIOperation,
    NormalizedAPIOperation,
    NormalizedAuthorizationPolicy,
    OpenAPIContractAnalysis,
    OpenAPIContractDetail,
    OpenAPIContractDiff,
    OpenAPIContractsPage,
    OpenAPIContractSummary,
    OpenAPIContractValidationResult,
    OpenAPIValidationIssue,
    OpenAPIValidationIssueCode,
    RegisteredOpenAPIContract,
    RegisteredServicesPage,
    RegisteredServiceSummary,
)

__all__ = (
    "ActivateOpenAPIContractCommand",
    "ActivateOpenAPIContractHandler",
    "AuthorizationManifest",
    "ChangedAPIOperation",
    "DiffOpenAPIContractHandler",
    "DiffOpenAPIContractQuery",
    "GetAuthorizationManifestHandler",
    "GetAuthorizationManifestQuery",
    "GetOpenAPIContractHandler",
    "GetOpenAPIContractQuery",
    "GetRegisteredServiceHandler",
    "GetRegisteredServiceQuery",
    "ListOpenAPIContractsHandler",
    "ListOpenAPIContractsQuery",
    "ListRegisteredServicesHandler",
    "ListRegisteredServicesQuery",
    "NormalizedAPIOperation",
    "NormalizedAuthorizationPolicy",
    "OpenAPIContractAnalysis",
    "OpenAPIContractAnalyzer",
    "OpenAPIContractDetail",
    "OpenAPIContractDiff",
    "OpenAPIContractDiffCalculator",
    "OpenAPIContractSummary",
    "OpenAPIContractValidationResult",
    "OpenAPIContractsPage",
    "OpenAPIValidationIssue",
    "OpenAPIValidationIssueCode",
    "RegisterOpenAPIContractCommand",
    "RegisterOpenAPIContractHandler",
    "RegisteredOpenAPIContract",
    "RegisteredServiceSummary",
    "RegisteredServicesPage",
    "RetireOpenAPIContractCommand",
    "RetireOpenAPIContractHandler",
    "ValidateOpenAPIContractCommand",
    "ValidateOpenAPIContractHandler",
)
