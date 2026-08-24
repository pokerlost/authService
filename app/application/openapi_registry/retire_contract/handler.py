"""Explicit OpenAPI contract retirement orchestration."""

from __future__ import annotations

from application.errors import (
    IntegrityError,
    OpenAPIContractActivationConflictError,
    OpenAPIContractNotFoundError,
    OpenAPIContractNotValidatedError,
)
from application.openapi_registry.values import OpenAPIContractSummary
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult, OpenAPIContractStatus
from persistence.database.models import OpenApiContractModel, RegisteredServiceModel
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyOpenAPIContractRepository,
    SQLAlchemyRegisteredServiceRepository,
)

from .command import RetireOpenAPIContractCommand


class RetireOpenAPIContractHandler:
    """Retire active or validated-never-active contracts without deleting history."""

    __slots__ = (
        "_audit_repository",
        "_clock",
        "_contract_repository",
        "_service_repository",
    )

    def __init__(
        self,
        *,
        service_repository: SQLAlchemyRegisteredServiceRepository,
        contract_repository: SQLAlchemyOpenAPIContractRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._service_repository = service_repository
        self._contract_repository = contract_repository
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(
        self,
        command: RetireOpenAPIContractCommand,
    ) -> OpenAPIContractSummary:
        """Leave no active manifest when retiring the active contract."""
        contract_hint = await self._contract_repository.get_by_id(command.contract_id)
        if contract_hint is None:
            raise OpenAPIContractNotFoundError
        service = await self._service_repository.get_by_id_for_update(
            contract_hint.registered_service_id
        )
        if service is None:
            raise IntegrityError
        contract = await self._contract_repository.get_by_id_for_update(command.contract_id)
        if contract is None or contract.registered_service_id != service.id:
            raise OpenAPIContractNotFoundError
        if contract.status is OpenAPIContractStatus.REGISTERED:
            raise OpenAPIContractNotValidatedError
        retired = contract
        if contract.status is not OpenAPIContractStatus.RETIRED:
            updated = await self._contract_repository.retire(
                contract_id=contract.id,
                retired_at=self._clock(),
            )
            if updated is None:
                raise OpenAPIContractActivationConflictError
            retired = updated
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=AuditEventType.OPENAPI_CONTRACT_RETIRED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="openapi_contract",
            target_id=str(contract.id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"serviceId": service.service_id},
        )
        return self._summary(retired, service)

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
