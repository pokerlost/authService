"""Atomic OpenAPI contract activation orchestration."""

from __future__ import annotations

from uuid import UUID

from application.audit import DurableAuditFailureRecorder
from application.errors import (
    ApplicationError,
    IntegrityError,
    OpenAPIContractActivationConflictError,
    OpenAPIContractNotFoundError,
    OpenAPIContractNotValidatedError,
    OpenAPIContractSecurityAcknowledgementRequiredError,
    OpenAPIOperationIDConflictError,
)
from application.openapi_registry.contract_diff_calculator import OpenAPIContractDiffCalculator
from application.openapi_registry.stored_operation_materializer import (
    materialize_stored_operations,
)
from application.openapi_registry.values import (
    NormalizedAPIOperation,
    OpenAPIContractDiff,
    OpenAPIContractSummary,
)
from application.time import UtcClock, utc_now
from domain.enums import (
    AuditEventType,
    AuditResult,
    OpenAPIContractStatus,
    SecurityChangeLevel,
)
from persistence.database.models import OpenApiContractModel, RegisteredServiceModel
from persistence.queries import SQLAlchemyOpenAPIRegistryQuery
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyOpenAPIContractRepository,
    SQLAlchemyOperationIdentityRepository,
    SQLAlchemyRegisteredServiceRepository,
)

from .command import ActivateOpenAPIContractCommand


class ActivateOpenAPIContractHandler:
    """Serialize activation, recheck diff and ownership, then replace the active contract."""

    __slots__ = (
        "_audit_repository",
        "_calculator",
        "_clock",
        "_contract_repository",
        "_failure_audit_recorder",
        "_operation_identity_repository",
        "_registry_query",
        "_service_repository",
    )

    def __init__(
        self,
        *,
        service_repository: SQLAlchemyRegisteredServiceRepository,
        contract_repository: SQLAlchemyOpenAPIContractRepository,
        operation_identity_repository: SQLAlchemyOperationIdentityRepository,
        registry_query: SQLAlchemyOpenAPIRegistryQuery,
        calculator: OpenAPIContractDiffCalculator,
        audit_repository: SQLAlchemyAuditEventRepository,
        failure_audit_recorder: DurableAuditFailureRecorder,
        clock: UtcClock = utc_now,
    ) -> None:
        self._service_repository = service_repository
        self._contract_repository = contract_repository
        self._operation_identity_repository = operation_identity_repository
        self._registry_query = registry_query
        self._calculator = calculator
        self._audit_repository = audit_repository
        self._failure_audit_recorder = failure_audit_recorder
        self._clock = clock

    async def execute(
        self,
        command: ActivateOpenAPIContractCommand,
    ) -> OpenAPIContractSummary:
        """Record success atomically or expected failure through a durable side transaction."""
        try:
            summary = await self._execute(command)
        except ApplicationError as exception:
            await self._failure_audit_recorder.append(
                event_type=AuditEventType.OPENAPI_CONTRACT_ACTIVATION_FAILED,
                context=command.audit_context,
                reason=exception.error_code,
                target_type="openapi_contract",
                target_id=command.contract_id,
            )
            raise
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=AuditEventType.OPENAPI_CONTRACT_ACTIVATION_SUCCEEDED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="openapi_contract",
            target_id=str(command.contract_id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"serviceId": summary.service_id},
        )
        return summary

    async def _execute(
        self,
        command: ActivateOpenAPIContractCommand,
    ) -> OpenAPIContractSummary:
        """Activate with TOCTOU protection and permanent global operation claims."""
        candidate_hint = await self._contract_repository.get_by_id(command.contract_id)
        if candidate_hint is None:
            raise OpenAPIContractNotFoundError
        service = await self._service_repository.get_by_id_for_update(
            candidate_hint.registered_service_id
        )
        if service is None:
            raise IntegrityError
        candidate = await self._contract_repository.get_by_id_for_update(command.contract_id)
        if candidate is None or candidate.registered_service_id != service.id:
            raise OpenAPIContractNotFoundError
        if candidate.status is OpenAPIContractStatus.REGISTERED:
            raise OpenAPIContractNotValidatedError

        current_active = await self._contract_repository.get_active_by_service_id(service.id)
        if candidate.status is OpenAPIContractStatus.ACTIVE:
            if current_active is None or current_active.id != candidate.id:
                raise IntegrityError
            retry_base = await self._load_retry_base(
                service=service,
                expected_base_contract_id=command.expected_base_contract_id,
            )
            diff = await self._calculate_diff(retry_base, candidate)
            self._verify_diff(command, diff)
            candidate_operations = await self._load_operations(candidate.id)
            await self._assert_and_claim_ownership(
                service=service,
                operations=candidate_operations,
            )
            return self._summary(candidate, service)

        current_active_id = current_active.id if current_active is not None else None
        if current_active_id != command.expected_base_contract_id:
            raise OpenAPIContractActivationConflictError
        diff = await self._calculate_diff(current_active, candidate)
        self._verify_diff(command, diff)
        candidate_operations = await self._load_operations(candidate.id)
        await self._assert_and_claim_ownership(
            service=service,
            operations=candidate_operations,
        )

        now = self._clock()
        if current_active is not None:
            retired = await self._contract_repository.retire(
                contract_id=current_active.id,
                retired_at=now,
            )
            if retired is None:
                raise OpenAPIContractActivationConflictError
        activated = await self._contract_repository.activate(
            contract_id=candidate.id,
            activated_at=now,
        )
        if activated is None:
            raise OpenAPIContractActivationConflictError
        return self._summary(activated, service)

    async def _load_retry_base(
        self,
        *,
        service: RegisteredServiceModel,
        expected_base_contract_id: UUID | None,
    ) -> OpenApiContractModel | None:
        if expected_base_contract_id is None:
            return None
        base = await self._contract_repository.get_by_id(expected_base_contract_id)
        if base is None or base.registered_service_id != service.id:
            raise OpenAPIContractActivationConflictError
        return base

    async def _calculate_diff(
        self,
        base: OpenApiContractModel | None,
        candidate: OpenApiContractModel,
    ) -> OpenAPIContractDiff:
        return self._calculator.calculate(
            base_contract_id=base.id if base is not None else None,
            candidate_contract_id=candidate.id,
            base_operations=await self._load_operations(base.id) if base is not None else [],
            candidate_operations=await self._load_operations(candidate.id),
        )

    async def _load_operations(self, contract_id: UUID) -> list[NormalizedAPIOperation]:
        return materialize_stored_operations(
            await self._registry_query.list_operation_policies(contract_id)
        )

    def _verify_diff(
        self,
        command: ActivateOpenAPIContractCommand,
        diff: OpenAPIContractDiff,
    ) -> None:
        if diff.diff_hash != command.expected_diff_hash:
            raise OpenAPIContractActivationConflictError
        if diff.security_change_level is SecurityChangeLevel.BREAKING:
            raise OpenAPIContractActivationConflictError
        if diff.requires_security_acknowledgement and not command.acknowledge_security_changes:
            raise OpenAPIContractSecurityAcknowledgementRequiredError

    async def _assert_and_claim_ownership(
        self,
        *,
        service: RegisteredServiceModel,
        operations: list[NormalizedAPIOperation],
    ) -> None:
        api_operation_ids = {operation.api_operation_id for operation in operations}
        existing = await self._operation_identity_repository.list_by_api_operation_ids(
            api_operation_ids
        )
        if any(row.registered_service_id != service.id for row in existing):
            raise OpenAPIOperationIDConflictError
        await self._operation_identity_repository.claim(
            api_operation_ids=api_operation_ids,
            registered_service_id=service.id,
        )
        claimed = await self._operation_identity_repository.list_by_api_operation_ids(
            api_operation_ids
        )
        if len(claimed) != len(api_operation_ids) or any(
            row.registered_service_id != service.id for row in claimed
        ):
            raise OpenAPIOperationIDConflictError

    def _summary(
        self,
        contract: OpenApiContractModel,
        service: RegisteredServiceModel,
    ) -> OpenAPIContractSummary:
        return OpenAPIContractSummary(
            contract_id=contract.id,
            service_id=service.service_id,
            contract_version=contract.contract_version,
            openapi_version=contract.openapi_version,
            schema_hash=contract.schema_hash,
            status=contract.status,
            validated_at=contract.validated_at,
            activated_at=contract.activated_at,
            retired_at=contract.retired_at,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
        )
