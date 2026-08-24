"""Immutable OpenAPI contract registration orchestration."""

from __future__ import annotations

from application.errors import (
    IntegrityError,
    OpenAPIContractRegistrationInvalidError,
    OpenAPIContractVersionConflictError,
)
from application.fingerprinting import canonical_fingerprint
from application.openapi_registry.contract_analyzer import OpenAPIContractAnalyzer
from application.openapi_registry.values import RegisteredOpenAPIContract
from application.time import UtcClock, utc_now
from domain.enums import AuditEventType, AuditResult
from persistence.database.models import OpenApiContractModel, RegisteredServiceModel
from persistence.repositories import (
    SQLAlchemyAuditEventRepository,
    SQLAlchemyOpenAPIContractRepository,
    SQLAlchemyRegisteredServiceRepository,
)

from .command import RegisterOpenAPIContractCommand


class RegisterOpenAPIContractHandler:
    """Onboard a service through one immutable bounded JSON contract."""

    __slots__ = (
        "_analyzer",
        "_audit_repository",
        "_clock",
        "_contract_repository",
        "_service_repository",
    )

    def __init__(
        self,
        *,
        analyzer: OpenAPIContractAnalyzer,
        service_repository: SQLAlchemyRegisteredServiceRepository,
        contract_repository: SQLAlchemyOpenAPIContractRepository,
        audit_repository: SQLAlchemyAuditEventRepository,
        clock: UtcClock = utc_now,
    ) -> None:
        self._analyzer = analyzer
        self._service_repository = service_repository
        self._contract_repository = contract_repository
        self._audit_repository = audit_repository
        self._clock = clock

    async def execute(
        self,
        command: RegisterOpenAPIContractCommand,
    ) -> RegisteredOpenAPIContract:
        """Create a registered row or return the existing equivalent contract."""
        analysis = self._analyzer.analyze(command.document)
        if (
            analysis.document_size_bytes is None
            or analysis.service_id is None
            or analysis.contract_version is None
            or analysis.openapi_version is None
        ):
            raise OpenAPIContractRegistrationInvalidError
        schema_hash = canonical_fingerprint(command.document)

        service = await self._service_repository.get_by_service_id(analysis.service_id)
        if service is None:
            service = await self._service_repository.create(analysis.service_id)
        if service is None:
            service = await self._service_repository.get_by_service_id(analysis.service_id)
        if service is None:
            raise IntegrityError

        existing = await self._existing_contract(
            service=service,
            contract_version=analysis.contract_version,
            schema_hash=schema_hash,
        )
        if existing is None:
            existing = await self._contract_repository.create(
                registered_service_id=service.id,
                contract_version=analysis.contract_version,
                openapi_version=analysis.openapi_version,
                schema_hash=schema_hash,
                document=command.document,
            )
        if existing is None:
            existing = await self._existing_contract(
                service=service,
                contract_version=analysis.contract_version,
                schema_hash=schema_hash,
            )
        if existing is None:
            raise IntegrityError
        context = command.audit_context
        await self._audit_repository.append(
            occurred_at=self._clock(),
            event_type=AuditEventType.OPENAPI_CONTRACT_REGISTERED,
            result=AuditResult.SUCCESS,
            actor_principal_id=context.actor_principal_id,
            actor_role=context.actor_role,
            target_type="openapi_contract",
            target_id=str(existing.id),
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            api_operation_id=context.api_operation_id,
            event_metadata={"serviceId": service.service_id},
        )
        return RegisteredOpenAPIContract(
            contract_id=existing.id,
            service_id=service.service_id,
            contract_version=existing.contract_version,
            schema_hash=existing.schema_hash,
            status=existing.status,
            created_at=existing.created_at,
        )

    async def _existing_contract(
        self,
        *,
        service: RegisteredServiceModel,
        contract_version: str,
        schema_hash: str,
    ) -> OpenApiContractModel | None:
        by_version = await self._contract_repository.get_by_service_and_version(
            registered_service_id=service.id,
            contract_version=contract_version,
        )
        if by_version is not None:
            if by_version.schema_hash != schema_hash:
                raise OpenAPIContractVersionConflictError
            return by_version
        return await self._contract_repository.get_by_service_and_schema_hash(
            registered_service_id=service.id,
            schema_hash=schema_hash,
        )
