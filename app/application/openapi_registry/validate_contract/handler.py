"""OpenAPI contract validation and atomic normalization orchestration."""

from __future__ import annotations

from application.errors import IntegrityError, OpenAPIContractNotFoundError
from application.openapi_registry.contract_analyzer import OpenAPIContractAnalyzer
from application.openapi_registry.values import (
    OpenAPIContractValidationResult,
    OpenAPIValidationIssue,
)
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult, OpenAPIContractStatus
from persistence.repositories import (
    SQLAlchemyAPIOperationRepository,
    SQLAlchemyAuditEventRepository,
    SQLAlchemyOpenAPIContractRepository,
    SQLAlchemyOperationIdentityRepository,
    SQLAlchemyRegisteredServiceRepository,
)

from .command import ValidateOpenAPIContractCommand


class ValidateOpenAPIContractHandler:
    """Persist normalized rows only after all contract and ownership checks pass."""

    __slots__ = (
        "_analyzer",
        "_audit_repository",
        "_clock",
        "_contract_repository",
        "_operation_identity_repository",
        "_operation_repository",
        "_service_repository",
    )

    def __init__(
        self,
        *,
        analyzer: OpenAPIContractAnalyzer,
        service_repository: SQLAlchemyRegisteredServiceRepository,
        contract_repository: SQLAlchemyOpenAPIContractRepository,
        operation_repository: SQLAlchemyAPIOperationRepository,
        operation_identity_repository: SQLAlchemyOperationIdentityRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._analyzer = analyzer
        self._service_repository = service_repository
        self._contract_repository = contract_repository
        self._operation_repository = operation_repository
        self._operation_identity_repository = operation_identity_repository
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(
        self,
        command: ValidateOpenAPIContractCommand,
    ) -> OpenAPIContractValidationResult:
        """Validate idempotently and normalize a registered valid contract once."""
        contract = await self._contract_repository.get_by_id_for_update(command.contract_id)
        if contract is None:
            raise OpenAPIContractNotFoundError
        service = await self._service_repository.get_by_id(contract.registered_service_id)
        if service is None:
            raise IntegrityError

        analysis = self._analyzer.analyze(contract.document)
        if (
            analysis.service_id != service.service_id
            or analysis.contract_version != contract.contract_version
            or analysis.openapi_version != contract.openapi_version
        ):
            raise IntegrityError
        issues = list(analysis.validation.issues)
        api_operation_ids = {operation.api_operation_id for operation in analysis.operations}
        ownership_rows = await self._operation_identity_repository.list_by_api_operation_ids(
            api_operation_ids
        )
        for ownership in ownership_rows:
            if ownership.registered_service_id != service.id:
                issues.append(
                    OpenAPIValidationIssue(
                        code="OPENAPI_OPERATION_ID_OWNED_BY_OTHER_SERVICE",
                        location="/paths",
                        message="An operationId is permanently owned by another service.",
                    )
                )

        result = OpenAPIContractValidationResult(valid=not issues, issues=issues)
        if not result.valid or contract.status is not OpenAPIContractStatus.REGISTERED:
            await self._append_audit(command, result)
            return result

        await self._operation_repository.create_for_contract(
            contract_id=contract.id,
            operations=analysis.operations,
        )
        validated = await self._contract_repository.mark_validated(
            contract_id=contract.id,
            validated_at=self._clock(),
        )
        if validated is None:
            raise IntegrityError
        await self._append_audit(command, result)
        return result

    async def _append_audit(
        self,
        command: ValidateOpenAPIContractCommand,
        result: OpenAPIContractValidationResult,
    ) -> None:
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=AuditEventType.OPENAPI_CONTRACT_VALIDATED,
            result=AuditResult.SUCCESS if result.valid else AuditResult.FAILURE,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="openapi_contract",
            target_id=str(command.contract_id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"valid": result.valid, "issueCount": len(result.issues)},
        )
