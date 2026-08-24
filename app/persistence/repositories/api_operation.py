"""SQLAlchemy normalized API operation repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from domain.openapi_registry import NormalizedAPIOperation
from persistence.database.models import ApiOperationModel

from .base import SQLAlchemyEntityRepository


class SQLAlchemyAPIOperationRepository(SQLAlchemyEntityRepository[ApiOperationModel]):
    """Persist contract-scoped operation identity and transport metadata."""

    model = ApiOperationModel

    async def create_for_contract(
        self,
        *,
        contract_id: UUID,
        operations: list[NormalizedAPIOperation],
    ) -> list[ApiOperationModel]:
        """Insert all normalized operations in one statement after complete validation."""
        if not operations:
            return []
        result = await self._read_scalar(
            insert(ApiOperationModel)
            .values(
                [
                    {
                        "contract_id": contract_id,
                        "api_operation_id": operation.api_operation_id,
                        "http_method": operation.http_method,
                        "path": operation.path,
                        "authorization_mode": operation.authorization.mode,
                        "required_scope": operation.authorization.required_scope,
                    }
                    for operation in operations
                ]
            )
            .returning(ApiOperationModel),
        )
        return result.all()

    async def list_by_contract_id(self, contract_id: UUID) -> list[ApiOperationModel]:
        """Return normalized operation entities in semantic ID order."""
        result = await self._read_scalar(
            select(ApiOperationModel)
            .where(ApiOperationModel.contract_id == contract_id)
            .order_by(ApiOperationModel.api_operation_id),
        )
        return result.all()
