"""SQLAlchemy append-only durable security audit repository."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Final
from uuid import UUID

from sqlalchemy import insert

from domain.enums import AuditEventType, AuditResult, Role
from persistence.database.models import AuditEventModel

from .base import SQLAlchemyRepository

_MAX_METADATA_BYTES: Final = 4_096
_FORBIDDEN_METADATA_KEY_PARTS: Final = (
    "accesstoken",
    "authorization",
    "clientsecret",
    "credentialdigest",
    "jwt",
    "nickname",
    "password",
    "pepper",
    "privatekey",
    "refreshtoken",
    "secret",
    "token",
    "username",
)


def _validate_metadata(value: dict[str, object]) -> None:
    """Reject oversized, non-JSON, or sensitive-key audit metadata."""
    pending: list[object] = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            for key, child in item.items():
                normalized_key = re.sub(r"[^a-z]", "", key.lower())
                if any(part in normalized_key for part in _FORBIDDEN_METADATA_KEY_PARTS):
                    raise ValueError("Audit metadata contains a forbidden sensitive key")
                pending.append(child)
        elif isinstance(item, list):
            pending.extend(item)
    try:
        encoded = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError):
        raise ValueError("Audit metadata must contain only JSON values") from None
    if len(encoded) > _MAX_METADATA_BYTES:
        raise ValueError("Audit metadata exceeds the byte limit")


class SQLAlchemyAuditEventRepository(SQLAlchemyRepository):
    """Append security audit events without update or delete capabilities."""

    async def append(
        self,
        *,
        occurred_at: datetime,
        event_type: AuditEventType,
        result: AuditResult,
        actor_principal_id: UUID | None = None,
        actor_role: Role | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        api_operation_id: str | None = None,
        event_metadata: dict[str, object] | None = None,
    ) -> AuditEventModel:
        """Insert and return one immutable safe audit event."""
        safe_metadata = event_metadata or {}
        _validate_metadata(safe_metadata)
        result_reader = await self._read_scalar(
            insert(AuditEventModel)
            .values(
                occurred_at=occurred_at,
                event_type=event_type,
                result=result,
                actor_principal_id=actor_principal_id,
                actor_role=actor_role,
                target_type=target_type,
                target_id=target_id,
                request_id=request_id,
                correlation_id=correlation_id,
                api_operation_id=api_operation_id,
                event_metadata=safe_metadata,
            )
            .returning(AuditEventModel),
        )
        return result_reader.one()
