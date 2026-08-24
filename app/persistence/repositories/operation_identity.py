"""SQLAlchemy permanent operation identity ownership repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from persistence.database.models import OperationIdentityModel

from .base import SQLAlchemyRepository


class SQLAlchemyOperationIdentityRepository(SQLAlchemyRepository):
    """Check and atomically claim globally owned semantic operation IDs."""

    async def list_by_api_operation_ids(
        self,
        api_operation_ids: set[str],
    ) -> list[OperationIdentityModel]:
        """Return existing ownership rows for a bounded candidate ID set."""
        if not api_operation_ids:
            return []
        result = await self._read_scalar(
            select(OperationIdentityModel)
            .where(OperationIdentityModel.api_operation_id.in_(api_operation_ids))
            .order_by(OperationIdentityModel.api_operation_id),
        )
        return result.all()

    async def claim(
        self,
        *,
        api_operation_ids: set[str],
        registered_service_id: UUID,
    ) -> list[str]:
        """Insert absent claims without overwriting a same- or different-owner row."""
        if not api_operation_ids:
            return []
        result = await self._read_scalar(
            insert(OperationIdentityModel)
            .values(
                [
                    {
                        "api_operation_id": api_operation_id,
                        "registered_service_id": registered_service_id,
                    }
                    for api_operation_id in sorted(api_operation_ids)
                ]
            )
            .on_conflict_do_nothing(index_elements=[OperationIdentityModel.api_operation_id])
            .returning(OperationIdentityModel.api_operation_id),
        )
        return result.all()
