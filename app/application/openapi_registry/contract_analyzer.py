"""Bounded generic PokerLost OpenAPI parser, validator, and normalizer."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Final, TypeGuard

from configuration.openapi_registry import OpenAPIRegistrySettings
from domain.enums import OperationAuthorizationMode
from domain.types import validate_api_operation_id, validate_contract_version, validate_service_id

from .values import (
    NormalizedAPIOperation,
    NormalizedAuthorizationPolicy,
    OpenAPIContractAnalysis,
    OpenAPIContractValidationResult,
    OpenAPIValidationIssue,
)

_OPENAPI_VERSION_PATTERN: Final = re.compile(r"3\.1\.\d+\Z")
_RPC_PATH_PATTERN: Final = re.compile(
    r"/(?P<namespace>[a-z][A-Za-z0-9]*)\.(?P<method>[a-z][A-Za-z0-9]*)\Z"
)
_HTTP_METHODS: Final = frozenset(
    {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
)
_SUPPORTED_HTTP_METHODS: Final = frozenset({"get", "post"})


def _is_json_object(value: object) -> TypeGuard[dict[str, object]]:
    """Narrow a runtime JSON object without transforming submitted values."""
    return isinstance(value, dict) and all(isinstance(key, str) for key in value)


def _is_json_array(value: object) -> TypeGuard[list[object]]:
    """Narrow a runtime JSON array."""
    return isinstance(value, list)


def _pointer_component(value: str) -> str:
    """Escape one JSON Pointer location component."""
    return value.replace("~", "~0").replace("/", "~1")


class OpenAPIContractAnalyzer:
    """Validate one submitted OpenAPI 3.1 JSON document without resolving remote data."""

    __slots__ = ("_settings",)

    def __init__(self, settings: OpenAPIRegistrySettings) -> None:
        self._settings = settings

    def analyze(self, document: dict[str, object]) -> OpenAPIContractAnalysis:
        """Return bounded identity facts, normalized operations, and finite issues."""
        document_size, bound_issues = self._validate_document_bounds(document)
        if bound_issues:
            return self._analysis(
                document_size=document_size,
                issues=bound_issues,
            )

        issues: list[OpenAPIValidationIssue] = []
        self._validate_refs(document, issues)
        openapi_version = self._validate_openapi_version(document, issues)
        service_id = self._validate_service_metadata(document, issues)
        contract_version = self._validate_info_version(document, issues)
        self._validate_webhooks(document, issues)

        paths = document.get("paths")
        if not _is_json_object(paths):
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_RPC_PATH_INVALID",
                    location="/paths",
                    message="OpenAPI paths must be an object.",
                )
            )
            return self._analysis(
                service_id=service_id,
                contract_version=contract_version,
                openapi_version=openapi_version,
                document_size=document_size,
                issues=issues,
            )

        operation_count = self._count_http_operations(paths)
        if operation_count > self._settings.max_operations:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_TOO_MANY_OPERATIONS",
                    location="/paths",
                    message="OpenAPI operation count exceeds the configured limit.",
                )
            )
            return self._analysis(
                service_id=service_id,
                contract_version=contract_version,
                openapi_version=openapi_version,
                document_size=document_size,
                issues=issues,
            )

        oauth2_scope_catalogs = self._oauth2_scope_catalogs(document, issues)
        top_level_security = document.get("security")
        seen_operation_ids: set[str] = set()
        operations: list[NormalizedAPIOperation] = []
        for path in sorted(paths):
            self._analyze_path(
                path=path,
                path_item_value=paths[path],
                service_id=service_id,
                top_level_security=top_level_security,
                oauth2_scope_catalogs=oauth2_scope_catalogs,
                seen_operation_ids=seen_operation_ids,
                operations=operations,
                issues=issues,
            )

        operations.sort(key=lambda operation: operation.api_operation_id)
        protected_scope_ids = {
            operation.authorization.required_scope
            for operation in operations
            if operation.authorization.required_scope is not None
        }
        operation_ids = {operation.api_operation_id for operation in operations}
        for flow_name, catalog in oauth2_scope_catalogs.items():
            for missing_scope in sorted(protected_scope_ids - catalog):
                issues.append(
                    OpenAPIValidationIssue(
                        code="OPENAPI_OAUTH2_SCOPE_MISSING",
                        location=(
                            "/components/securitySchemes/OAuth2/flows/"
                            f"{flow_name}/scopes/{_pointer_component(missing_scope)}"
                        ),
                        message="Every protected operation scope must be declared by the flow.",
                    )
                )
            for extra_scope in sorted(catalog - operation_ids):
                issues.append(
                    OpenAPIValidationIssue(
                        code="OPENAPI_OAUTH2_SCOPE_INVALID",
                        location=(
                            "/components/securitySchemes/OAuth2/flows/"
                            f"{flow_name}/scopes/{_pointer_component(extra_scope)}"
                        ),
                        message="OAuth2 scope catalog entries must identify contract operations.",
                    )
                )
        return self._analysis(
            service_id=service_id,
            contract_version=contract_version,
            openapi_version=openapi_version,
            document_size=document_size,
            operations=operations,
            issues=issues,
        )

    def _validate_document_bounds(
        self,
        document: dict[str, object],
    ) -> tuple[int | None, list[OpenAPIValidationIssue]]:
        issues: list[OpenAPIValidationIssue] = []
        stack: list[tuple[object, int]] = [(document, 1)]
        visited_nodes = 0
        while stack:
            value, depth = stack.pop()
            visited_nodes += 1
            if depth > self._settings.max_nesting_depth:
                issues.append(
                    OpenAPIValidationIssue(
                        code="OPENAPI_NESTING_TOO_DEEP",
                        location="/",
                        message="OpenAPI nesting depth exceeds the configured limit.",
                    )
                )
                return None, issues
            if visited_nodes > self._settings.max_document_bytes:
                issues.append(
                    OpenAPIValidationIssue(
                        code="OPENAPI_DOCUMENT_TOO_LARGE",
                        location="/",
                        message="OpenAPI document exceeds the configured size limit.",
                    )
                )
                return None, issues
            if _is_json_object(value):
                stack.extend((child, depth + 1) for child in value.values())
            elif _is_json_array(value):
                stack.extend((child, depth + 1) for child in value)
            elif value is not None and not isinstance(value, str | int | float | bool):
                issues.append(
                    OpenAPIValidationIssue(
                        code="OPENAPI_DOCUMENT_INVALID",
                        location="/",
                        message="OpenAPI document must contain only JSON values.",
                    )
                )
                return None, issues

        try:
            encoded = json.dumps(
                document,
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        except (TypeError, ValueError):
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_DOCUMENT_INVALID",
                    location="/",
                    message="OpenAPI document must be canonical JSON.",
                )
            )
            return None, issues
        document_size = len(encoded)
        if document_size > self._settings.max_document_bytes:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_DOCUMENT_TOO_LARGE",
                    location="/",
                    message="OpenAPI document exceeds the configured size limit.",
                )
            )
        return document_size, issues

    def _validate_refs(
        self,
        document: dict[str, object],
        issues: list[OpenAPIValidationIssue],
    ) -> None:
        stack: list[tuple[object, str]] = [(document, "")]
        while stack:
            value, location = stack.pop()
            if _is_json_object(value):
                reference = value.get("$ref")
                if reference is not None and (
                    not isinstance(reference, str) or not reference.startswith("#/components/")
                ):
                    issues.append(
                        OpenAPIValidationIssue(
                            code="OPENAPI_EXTERNAL_REF_FORBIDDEN",
                            location=f"{location}/$ref" or "/$ref",
                            message="Only local #/components references are allowed.",
                        )
                    )
                for key, child in value.items():
                    stack.append((child, f"{location}/{_pointer_component(key)}"))
            elif _is_json_array(value):
                for index, child in enumerate(value):
                    stack.append((child, f"{location}/{index}"))

    def _validate_openapi_version(
        self,
        document: Mapping[str, object],
        issues: list[OpenAPIValidationIssue],
    ) -> str | None:
        value = document.get("openapi")
        if (
            not isinstance(value, str)
            or not 1 <= len(value) <= 16
            or _OPENAPI_VERSION_PATTERN.fullmatch(value) is None
        ):
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_VERSION_UNSUPPORTED",
                    location="/openapi",
                    message="Registry v1 supports only OpenAPI 3.1.x.",
                )
            )
            return value if isinstance(value, str) and 1 <= len(value) <= 16 else None
        return value

    def _validate_service_metadata(
        self,
        document: Mapping[str, object],
        issues: list[OpenAPIValidationIssue],
    ) -> str | None:
        if "x-pokerlost-service" not in document:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_SERVICE_METADATA_MISSING",
                    location="/x-pokerlost-service",
                    message="PokerLost service metadata is required.",
                )
            )
            return None
        metadata = document["x-pokerlost-service"]
        if not _is_json_object(metadata) or set(metadata) != {"id"}:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_SERVICE_METADATA_INVALID",
                    location="/x-pokerlost-service",
                    message="PokerLost service metadata must contain exactly id.",
                )
            )
            return None
        try:
            return validate_service_id(metadata["id"])
        except ValueError:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_SERVICE_METADATA_INVALID",
                    location="/x-pokerlost-service/id",
                    message="PokerLost service ID is invalid.",
                )
            )
            return None

    def _validate_info_version(
        self,
        document: Mapping[str, object],
        issues: list[OpenAPIValidationIssue],
    ) -> str | None:
        info = document.get("info")
        if not _is_json_object(info):
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_INFO_VERSION_MISSING",
                    location="/info/version",
                    message="OpenAPI info.version is required.",
                )
            )
            return None
        try:
            return validate_contract_version(info.get("version"))
        except ValueError:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_INFO_VERSION_MISSING",
                    location="/info/version",
                    message="OpenAPI info.version must be non-empty and bounded.",
                )
            )
            return None

    def _validate_webhooks(
        self,
        document: Mapping[str, object],
        issues: list[OpenAPIValidationIssue],
    ) -> None:
        webhooks = document.get("webhooks")
        if webhooks:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_WEBHOOKS_UNSUPPORTED",
                    location="/webhooks",
                    message="Executable OpenAPI webhooks are unsupported by registry v1.",
                )
            )

    def _count_http_operations(self, paths: Mapping[str, object]) -> int:
        count = 0
        for path_item in paths.values():
            if not _is_json_object(path_item):
                continue
            count += sum(key.lower() in _HTTP_METHODS for key in path_item)
            if count > self._settings.max_operations:
                return count
        return count

    def _oauth2_scope_catalogs(
        self,
        document: Mapping[str, object],
        issues: list[OpenAPIValidationIssue],
    ) -> dict[str, frozenset[str]]:
        location = "/components/securitySchemes/OAuth2"
        components = document.get("components")
        if not _is_json_object(components):
            self._missing_oauth2_scheme(location, issues)
            return {}
        security_schemes = components.get("securitySchemes")
        if not _is_json_object(security_schemes):
            self._missing_oauth2_scheme(location, issues)
            return {}
        scheme = security_schemes.get("OAuth2")
        if scheme is None:
            self._missing_oauth2_scheme(location, issues)
            return {}
        if not _is_json_object(scheme) or scheme.get("type") != "oauth2":
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_OAUTH2_SECURITY_SCHEME_INVALID",
                    location=location,
                    message="OAuth2 must be the canonical oauth2 security scheme.",
                )
            )
            return {}
        flows = scheme.get("flows")
        if not _is_json_object(flows) or set(flows) != {"password", "clientCredentials"}:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_OAUTH2_SECURITY_SCHEME_INVALID",
                    location=f"{location}/flows",
                    message="OAuth2 must define only password and clientCredentials flows.",
                )
            )
            return {}

        catalogs: dict[str, frozenset[str]] = {}
        for flow_name in ("password", "clientCredentials"):
            flow = flows[flow_name]
            flow_location = f"{location}/flows/{flow_name}"
            if not _is_json_object(flow) or flow.get("tokenUrl") != "/oauth.token":
                issues.append(
                    OpenAPIValidationIssue(
                        code="OPENAPI_OAUTH2_SECURITY_SCHEME_INVALID",
                        location=flow_location,
                        message="OAuth2 flow tokenUrl must be /oauth.token.",
                    )
                )
                continue
            scopes = flow.get("scopes")
            if not _is_json_object(scopes) or not all(
                isinstance(description, str) for description in scopes.values()
            ):
                issues.append(
                    OpenAPIValidationIssue(
                        code="OPENAPI_OAUTH2_SECURITY_SCHEME_INVALID",
                        location=f"{flow_location}/scopes",
                        message="OAuth2 flow scopes must be a JSON string map.",
                    )
                )
                continue
            valid_scopes: set[str] = set()
            for scope in scopes:
                try:
                    valid_scopes.add(validate_api_operation_id(scope))
                except ValueError:
                    issues.append(
                        OpenAPIValidationIssue(
                            code="OPENAPI_OAUTH2_SCOPE_INVALID",
                            location=f"{flow_location}/scopes/{_pointer_component(scope)}",
                            message="OAuth2 scope must be a canonical operationId.",
                        )
                    )
            catalogs[flow_name] = frozenset(valid_scopes)
        return catalogs

    def _missing_oauth2_scheme(
        self,
        location: str,
        issues: list[OpenAPIValidationIssue],
    ) -> None:
        issues.append(
            OpenAPIValidationIssue(
                code="OPENAPI_OAUTH2_SECURITY_SCHEME_MISSING",
                location=location,
                message="Canonical OAuth2 security scheme is required.",
            )
        )

    def _analyze_path(
        self,
        *,
        path: str,
        path_item_value: object,
        service_id: str | None,
        top_level_security: object,
        oauth2_scope_catalogs: dict[str, frozenset[str]],
        seen_operation_ids: set[str],
        operations: list[NormalizedAPIOperation],
        issues: list[OpenAPIValidationIssue],
    ) -> None:
        path_location = f"/paths/{_pointer_component(path)}"
        if not _is_json_object(path_item_value):
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_RPC_PATH_INVALID",
                    location=path_location,
                    message="OpenAPI path item must be directly analyzable.",
                )
            )
            return
        if "$ref" in path_item_value:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_REF_UNSUPPORTED",
                    location=f"{path_location}/$ref",
                    message="Referenced Path Items are unsupported by registry v1.",
                )
            )

        method_keys = [key for key in path_item_value if key.lower() in _HTTP_METHODS]
        if len(method_keys) != 1:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_RPC_PATH_INVALID",
                    location=path_location,
                    message="Each RPC path must contain exactly one HTTP operation.",
                )
            )
            return
        raw_method = method_keys[0]
        method = raw_method.lower()
        if raw_method != method or method not in _SUPPORTED_HTTP_METHODS:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_HTTP_METHOD_UNSUPPORTED",
                    location=f"{path_location}/{_pointer_component(raw_method)}",
                    message="Registry v1 supports only lowercase GET and POST operations.",
                )
            )
            return

        expected_operation_id: str | None = None
        if path == "/":
            if method != "get":
                issues.append(
                    OpenAPIValidationIssue(
                        code="OPENAPI_RPC_PATH_INVALID",
                        location=path_location,
                        message="The service root must contain exactly one GET operation.",
                    )
                )
            if service_id is not None:
                expected_operation_id = f"{service_id}.root"
        else:
            match = _RPC_PATH_PATTERN.fullmatch(path)
            if match is None:
                issues.append(
                    OpenAPIValidationIssue(
                        code="OPENAPI_RPC_PATH_INVALID",
                        location=path_location,
                        message="Path must follow the dotted camelCase RPC convention.",
                    )
                )
            elif service_id is not None:
                expected_operation_id = (
                    f"{service_id}.{match.group('namespace')}.{match.group('method')}"
                )

        operation_value = path_item_value[raw_method]
        operation_location = f"{path_location}/{method}"
        if not _is_json_object(operation_value):
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_OPERATION_ID_MISSING",
                    location=f"{operation_location}/operationId",
                    message="OpenAPI operation must be directly analyzable.",
                )
            )
            return
        if "$ref" in operation_value:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_REF_UNSUPPORTED",
                    location=f"{operation_location}/$ref",
                    message="Referenced Operations are unsupported by registry v1.",
                )
            )
        if operation_value.get("callbacks"):
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_CALLBACKS_UNSUPPORTED",
                    location=f"{operation_location}/callbacks",
                    message="Executable OpenAPI callbacks are unsupported by registry v1.",
                )
            )

        operation_id = operation_value.get("operationId")
        if not isinstance(operation_id, str) or not operation_id:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_OPERATION_ID_MISSING",
                    location=f"{operation_location}/operationId",
                    message="Every HTTP operation requires operationId.",
                )
            )
            return
        try:
            validate_api_operation_id(operation_id)
        except ValueError:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_OPERATION_ID_INVALID",
                    location=f"{operation_location}/operationId",
                    message="OpenAPI operationId is not a bounded dotted identifier.",
                )
            )
        if expected_operation_id is not None and operation_id != expected_operation_id:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_OPERATION_ID_INVALID",
                    location=f"{operation_location}/operationId",
                    message="OpenAPI operationId does not match its service and RPC path.",
                )
            )
        if operation_id in seen_operation_ids:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_OPERATION_ID_DUPLICATE",
                    location=f"{operation_location}/operationId",
                    message="OpenAPI operationId is duplicated within the contract.",
                )
            )
        seen_operation_ids.add(operation_id)

        if "x-pokerlost-authz" in operation_value:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_SECURITY_MISMATCH",
                    location=f"{operation_location}/x-pokerlost-authz",
                    message="Legacy x-pokerlost-authz metadata is forbidden.",
                )
            )
        effective_security = operation_value.get("security", top_level_security)
        policy = self._parse_authorization(
            operation_id=operation_id,
            effective_security=effective_security,
            oauth2_scope_catalogs=oauth2_scope_catalogs,
            operation_location=operation_location,
            issues=issues,
        )
        if policy is None:
            return
        try:
            operation = NormalizedAPIOperation(
                api_operation_id=operation_id,
                http_method=method.upper(),
                path=path,
                authorization=policy,
            )
        except ValueError:
            return
        operations.append(operation)

    def _parse_authorization(
        self,
        *,
        operation_id: str,
        effective_security: object,
        oauth2_scope_catalogs: dict[str, frozenset[str]],
        operation_location: str,
        issues: list[OpenAPIValidationIssue],
    ) -> NormalizedAuthorizationPolicy | None:
        location = f"{operation_location}/security"
        catalog = frozenset().union(*oauth2_scope_catalogs.values())
        if effective_security is None or effective_security == []:
            if operation_id in catalog:
                issues.append(
                    OpenAPIValidationIssue(
                        code="OPENAPI_SECURITY_MISMATCH",
                        location=location,
                        message="A catalogued protected operation cannot use empty security.",
                    )
                )
            return NormalizedAuthorizationPolicy(mode=OperationAuthorizationMode.PUBLIC)
        if not _is_json_array(effective_security) or len(effective_security) != 1:
            self._invalid_security(location, issues)
            return None
        requirement = effective_security[0]
        if not _is_json_object(requirement) or set(requirement) != {"OAuth2"}:
            self._invalid_security(location, issues)
            return None
        scopes = requirement["OAuth2"]
        if not _is_json_array(scopes) or not scopes:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_OAUTH2_SCOPE_MISSING",
                    location=f"{location}/0/OAuth2",
                    message="Protected operation requires exactly one OAuth2 scope.",
                )
            )
            return None
        if len(scopes) != 1 or not isinstance(scopes[0], str):
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_OAUTH2_SCOPE_INVALID",
                    location=f"{location}/0/OAuth2",
                    message="Protected operation requires exactly one string OAuth2 scope.",
                )
            )
            return None
        required_scope = scopes[0]
        if required_scope != operation_id:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_OAUTH2_SCOPE_OPERATION_MISMATCH",
                    location=f"{location}/0/OAuth2/0",
                    message="Required OAuth2 scope must equal operationId.",
                )
            )
            return None
        if required_scope not in catalog:
            issues.append(
                OpenAPIValidationIssue(
                    code="OPENAPI_OAUTH2_SCOPE_MISSING",
                    location=f"{location}/0/OAuth2/0",
                    message="Required OAuth2 scope is absent from the flow scope catalog.",
                )
            )
            return None
        return NormalizedAuthorizationPolicy(
            mode=OperationAuthorizationMode.OAUTH2,
            required_scope=required_scope,
        )

    def _invalid_security(
        self,
        location: str,
        issues: list[OpenAPIValidationIssue],
    ) -> None:
        issues.append(
            OpenAPIValidationIssue(
                code="OPENAPI_SECURITY_MISMATCH",
                location=location,
                message="Operation security must be empty or one canonical OAuth2 requirement.",
            )
        )

    def _analysis(
        self,
        *,
        service_id: str | None = None,
        contract_version: str | None = None,
        openapi_version: str | None = None,
        document_size: int | None = None,
        operations: list[NormalizedAPIOperation] | None = None,
        issues: list[OpenAPIValidationIssue],
    ) -> OpenAPIContractAnalysis:
        return OpenAPIContractAnalysis(
            service_id=service_id,
            contract_version=contract_version,
            openapi_version=openapi_version,
            document_size_bytes=document_size,
            operations=operations or [],
            validation=OpenAPIContractValidationResult(
                valid=not issues,
                issues=issues,
            ),
        )
