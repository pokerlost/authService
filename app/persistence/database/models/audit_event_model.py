"""Append-only durable security audit event."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Index, String, func, text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import AuditEventType, AuditResult, Role
from persistence.database import UUIDModel


class AuditEventModel(UUIDModel):
    """Immutable durable record of a security-sensitive outcome."""

    __tablename__ = "audit_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ("
            "'user_registered', 'password_grant_succeeded', 'password_grant_failed', "
            "'client_credentials_succeeded', 'client_credentials_failed', "
            "'oauth_token_refreshed', 'oauth_refresh_reuse_detected', "
            "'session_revoked', 'all_sessions_revoked', 'password_changed', "
            "'password_reset_by_master', 'support_account_created', "
            "'master_account_created', 'account_disabled', 'account_enabled', "
            "'service_principal_created', 'service_credential_created', "
            "'service_credential_revoked', 'service_audience_granted', "
            "'service_audience_revoked', 'service_scope_granted', "
            "'service_scope_revoked', 'role_scope_granted', 'role_scope_revoked', "
            "'openapi_contract_registered', 'openapi_contract_validated', "
            "'openapi_contract_activation_succeeded', "
            "'openapi_contract_activation_failed', 'openapi_contract_retired')",
            name="ck_audit_events_event_type",
        ),
        CheckConstraint(
            "result IN ('success', 'failure')",
            name="ck_audit_events_result",
        ),
        CheckConstraint(
            "actor_role IS NULL OR actor_role IN ('user', 'support', 'master', 'auto')",
            name="ck_audit_events_actor_role",
        ),
        CheckConstraint(
            "jsonb_typeof(metadata) = 'object'",
            name="ck_audit_events_metadata_object",
        ),
        Index("ix_audit_events_occurred_at_id", "occurred_at", "id"),
        Index("ix_audit_events_event_type_occurred_at", "event_type", "occurred_at"),
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    event_type: Mapped[AuditEventType] = mapped_column(
        SQLAlchemyEnum(
            AuditEventType,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=64,
            validate_strings=True,
        ),
        nullable=False,
    )
    result: Mapped[AuditResult] = mapped_column(
        SQLAlchemyEnum(
            AuditResult,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=7,
            validate_strings=True,
        ),
        nullable=False,
    )
    actor_principal_id: Mapped[UUID | None]
    actor_role: Mapped[Role | None] = mapped_column(
        SQLAlchemyEnum(
            Role,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=7,
            validate_strings=True,
        )
    )
    target_type: Mapped[str | None] = mapped_column(String(64))
    target_id: Mapped[str | None] = mapped_column(String(255))
    request_id: Mapped[str | None] = mapped_column(String(128))
    correlation_id: Mapped[str | None] = mapped_column(String(128))
    api_operation_id: Mapped[str | None] = mapped_column(String(255))
    event_metadata: Mapped[dict[str, object]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
