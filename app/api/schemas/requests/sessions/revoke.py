"""Owned-session revocation request."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from api.schemas.base import APIModel
from application.audit import AuditContext
from application.sessions import RevokeSessionCommand


class RevokeSessionRequest(APIModel):
    """Target session identifier without a caller-supplied owner identity."""

    session_id: UUID = Field(description="Owned session identifier to revoke.")

    def to_command(
        self,
        *,
        principal_id: UUID,
        audit_context: AuditContext,
    ) -> RevokeSessionCommand:
        """Add the server-authenticated owner to the session revocation command."""
        return RevokeSessionCommand(
            principal_id=principal_id,
            session_id=self.session_id,
            audit_context=audit_context,
        )
