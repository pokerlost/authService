"""SQLAlchemy source-service OAuth2 scope grant repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from persistence.database.models import ServiceScopeGrantModel

from .base import SQLAlchemyRepository


class SQLAlchemyServiceScopeGrantRepository(SQLAlchemyRepository):
    """Persist exact source, target audience, and operation scope grants."""

    async def grant(
        self,
        *,
        service_principal_id: UUID,
        audience: str,
        api_operation_id: str,
    ) -> bool:
        """Idempotently grant one service scope and report whether it was created."""
        result = await self._read_scalar(
            insert(ServiceScopeGrantModel)
            .values(
                service_principal_id=service_principal_id,
                audience=audience,
                api_operation_id=api_operation_id,
            )
            .on_conflict_do_nothing(
                index_elements=[
                    ServiceScopeGrantModel.service_principal_id,
                    ServiceScopeGrantModel.audience,
                    ServiceScopeGrantModel.api_operation_id,
                ]
            )
            .returning(ServiceScopeGrantModel.api_operation_id),
        )
        return result.one_or_none() is not None

    async def revoke(
        self,
        *,
        service_principal_id: UUID,
        audience: str,
        api_operation_id: str,
    ) -> bool:
        """Idempotently revoke one service scope and report whether it was removed."""
        result = await self._read_scalar(
            delete(ServiceScopeGrantModel)
            .where(
                ServiceScopeGrantModel.service_principal_id == service_principal_id,
                ServiceScopeGrantModel.audience == audience,
                ServiceScopeGrantModel.api_operation_id == api_operation_id,
            )
            .returning(ServiceScopeGrantModel.api_operation_id),
        )
        return result.one_or_none() is not None

    async def list_for_service_resource(
        self,
        *,
        service_principal_id: UUID,
        audience: str,
        limit: int,
    ) -> list[ServiceScopeGrantModel]:
        """Return a bounded deterministic grant list for one source and resource."""
        result = await self._read_scalar(
            select(ServiceScopeGrantModel)
            .where(
                ServiceScopeGrantModel.service_principal_id == service_principal_id,
                ServiceScopeGrantModel.audience == audience,
            )
            .order_by(ServiceScopeGrantModel.api_operation_id)
            .limit(limit),
        )
        return result.all()
