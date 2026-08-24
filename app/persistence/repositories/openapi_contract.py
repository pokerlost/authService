"""SQLAlchemy immutable OpenAPI contract repository."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert

from domain.enums import OpenAPIContractStatus
from domain.types import ContractVersion
from persistence.database.models import OpenApiContractModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyOpenAPIContractRepository(SQLAlchemyEntityRepository[OpenApiContractModel]):
    """Persist immutable JSON contracts and explicit lifecycle timestamps."""

    model = OpenApiContractModel

    async def create(
        self,
        *,
        registered_service_id: UUID,
        contract_version: ContractVersion,
        openapi_version: str,
        schema_hash: str,
        document: dict[str, object],
    ) -> OpenApiContractModel | None:
        """Insert a registered contract or return no row on a uniqueness race."""
        result = await self._read_scalar(
            insert(OpenApiContractModel)
            .values(
                registered_service_id=registered_service_id,
                contract_version=contract_version,
                openapi_version=openapi_version,
                schema_hash=schema_hash,
                document=document,
                status=OpenAPIContractStatus.REGISTERED,
            )
            .on_conflict_do_nothing()
            .returning(OpenApiContractModel),
        )
        return result.one_or_none()

    async def get_by_id_for_update(self, contract_id: UUID) -> OpenApiContractModel | None:
        """Lock one contract before normalization or lifecycle mutation."""
        result = await self._read_scalar(
            select(OpenApiContractModel)
            .where(OpenApiContractModel.id == contract_id)
            .with_for_update(),
        )
        return result.one_or_none()

    async def get_by_service_and_version(
        self,
        *,
        registered_service_id: UUID,
        contract_version: ContractVersion,
    ) -> OpenApiContractModel | None:
        """Find an immutable contract by its service-scoped version identity."""
        result = await self._read_scalar(
            select(OpenApiContractModel).where(
                OpenApiContractModel.registered_service_id == registered_service_id,
                OpenApiContractModel.contract_version == contract_version,
            ),
        )
        return result.one_or_none()

    async def get_by_service_and_schema_hash(
        self,
        *,
        registered_service_id: UUID,
        schema_hash: str,
    ) -> OpenApiContractModel | None:
        """Find an equivalent semantic JSON schema for one service."""
        result = await self._read_scalar(
            select(OpenApiContractModel).where(
                OpenApiContractModel.registered_service_id == registered_service_id,
                OpenApiContractModel.schema_hash == schema_hash,
            ),
        )
        return result.one_or_none()

    async def get_active_by_service_id(
        self,
        registered_service_id: UUID,
    ) -> OpenApiContractModel | None:
        """Return the sole DB-enforced active contract for one service."""
        result = await self._read_scalar(
            select(OpenApiContractModel).where(
                OpenApiContractModel.registered_service_id == registered_service_id,
                OpenApiContractModel.status == OpenAPIContractStatus.ACTIVE,
            ),
        )
        return result.one_or_none()

    async def mark_validated(
        self,
        *,
        contract_id: UUID,
        validated_at: datetime,
    ) -> OpenApiContractModel | None:
        """Transition only a registered contract after atomic normalization."""
        result = await self._read_scalar(
            update(OpenApiContractModel)
            .where(
                OpenApiContractModel.id == contract_id,
                OpenApiContractModel.status == OpenAPIContractStatus.REGISTERED,
            )
            .values(
                status=OpenAPIContractStatus.VALIDATED,
                validated_at=validated_at,
            )
            .returning(OpenApiContractModel),
        )
        return result.one_or_none()

    async def activate(
        self,
        *,
        contract_id: UUID,
        activated_at: datetime,
    ) -> OpenApiContractModel | None:
        """Activate a validated or retired immutable contract, including explicit rollback."""
        result = await self._read_scalar(
            update(OpenApiContractModel)
            .where(
                OpenApiContractModel.id == contract_id,
                OpenApiContractModel.status.in_(
                    (OpenAPIContractStatus.VALIDATED, OpenAPIContractStatus.RETIRED)
                ),
            )
            .values(
                status=OpenAPIContractStatus.ACTIVE,
                activated_at=activated_at,
                retired_at=None,
            )
            .returning(OpenApiContractModel),
        )
        return result.one_or_none()

    async def retire(
        self,
        *,
        contract_id: UUID,
        retired_at: datetime,
    ) -> OpenApiContractModel | None:
        """Idempotently retire a validated, active, or already retired contract."""
        result = await self._read_scalar(
            update(OpenApiContractModel)
            .where(
                OpenApiContractModel.id == contract_id,
                OpenApiContractModel.status.in_(
                    (
                        OpenAPIContractStatus.VALIDATED,
                        OpenAPIContractStatus.ACTIVE,
                        OpenAPIContractStatus.RETIRED,
                    )
                ),
            )
            .values(
                status=OpenAPIContractStatus.RETIRED,
                retired_at=func.coalesce(OpenApiContractModel.retired_at, retired_at),
            )
            .returning(OpenApiContractModel),
        )
        return result.one_or_none()
