"""Persisted immutable OpenAPI JSON contract."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import OpenAPIContractStatus
from persistence.database import UUIDModel
from persistence.database.mixins import TimestampMixin


class OpenApiContractModel(TimestampMixin, UUIDModel):
    """Immutable submitted schema with mutable validated activation lifecycle metadata."""

    __tablename__ = "openapi_contracts"
    __table_args__ = (
        CheckConstraint(
            "char_length(contract_version) BETWEEN 1 AND 64",
            name="ck_openapi_contracts_contract_version_length",
        ),
        CheckConstraint(
            "char_length(openapi_version) BETWEEN 1 AND 16",
            name="ck_openapi_contracts_openapi_version_length",
        ),
        CheckConstraint(
            "schema_hash ~ '^[0-9a-f]{64}$'",
            name="ck_openapi_contracts_schema_hash_format",
        ),
        CheckConstraint(
            "status IN ('registered', 'validated', 'active', 'retired')",
            name="ck_openapi_contracts_status",
        ),
        CheckConstraint(
            "(status = 'registered' AND validated_at IS NULL AND activated_at IS NULL "
            "AND retired_at IS NULL) OR "
            "(status = 'validated' AND validated_at IS NOT NULL AND activated_at IS NULL "
            "AND retired_at IS NULL) OR "
            "(status = 'active' AND validated_at IS NOT NULL AND activated_at IS NOT NULL "
            "AND retired_at IS NULL) OR "
            "(status = 'retired' AND validated_at IS NOT NULL AND retired_at IS NOT NULL)",
            name="ck_openapi_contracts_lifecycle",
        ),
        UniqueConstraint(
            "registered_service_id",
            "contract_version",
            name="uq_openapi_contracts_service_version",
        ),
        UniqueConstraint(
            "registered_service_id",
            "schema_hash",
            name="uq_openapi_contracts_service_schema_hash",
        ),
        Index(
            "uq_openapi_contracts_one_active_service",
            "registered_service_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )

    registered_service_id: Mapped[UUID] = mapped_column(
        ForeignKey("registered_services.id", ondelete="RESTRICT"),
        nullable=False,
    )
    contract_version: Mapped[str] = mapped_column(String(64), nullable=False)
    openapi_version: Mapped[str] = mapped_column(String(16), nullable=False)
    schema_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    document: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    status: Mapped[OpenAPIContractStatus] = mapped_column(
        SQLAlchemyEnum(
            OpenAPIContractStatus,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=10,
            validate_strings=True,
        ),
        nullable=False,
    )
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
