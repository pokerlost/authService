"""Persisted normalized OpenAPI HTTP operation."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import OperationAuthorizationMode
from persistence.database import UUIDModel
from persistence.database.mixins import CreatedAtMixin


class ApiOperationModel(CreatedAtMixin, UUIDModel):
    """Contract-scoped semantic operation plus transport metadata."""

    __tablename__ = "api_operations"
    __table_args__ = (
        CheckConstraint(
            "char_length(api_operation_id) BETWEEN 3 AND 255",
            name="ck_api_operations_api_operation_id_length",
        ),
        CheckConstraint(
            "api_operation_id ~ '^[a-z][A-Za-z0-9]{1,62}(\\.[a-z][A-Za-z0-9]{0,62}){1,2}$'",
            name="ck_api_operations_api_operation_id_format",
        ),
        CheckConstraint(
            "http_method IN ('GET', 'POST')",
            name="ck_api_operations_http_method",
        ),
        CheckConstraint(
            "char_length(path) BETWEEN 1 AND 255 AND left(path, 1) = '/'",
            name="ck_api_operations_path",
        ),
        CheckConstraint(
            "authorization_mode IN ('public', 'oauth2')",
            name="ck_api_operations_authorization_mode",
        ),
        CheckConstraint(
            "(authorization_mode = 'public' AND required_scope IS NULL) OR "
            "(authorization_mode = 'oauth2' AND required_scope = api_operation_id)",
            name="ck_api_operations_authorization_variant",
        ),
        UniqueConstraint(
            "contract_id",
            "api_operation_id",
            name="uq_api_operations_contract_operation_id",
        ),
        UniqueConstraint(
            "contract_id",
            "http_method",
            "path",
            name="uq_api_operations_contract_method_path",
        ),
    )

    contract_id: Mapped[UUID] = mapped_column(
        ForeignKey("openapi_contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    api_operation_id: Mapped[str] = mapped_column(String(255), nullable=False)
    http_method: Mapped[str] = mapped_column(String(4), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    authorization_mode: Mapped[OperationAuthorizationMode] = mapped_column(
        SQLAlchemyEnum(
            OperationAuthorizationMode,
            values_callable=lambda enum: [member.value for member in enum],
            native_enum=False,
            length=6,
            validate_strings=True,
        ),
        nullable=False,
    )
    required_scope: Mapped[str | None] = mapped_column(String(255))
