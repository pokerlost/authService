"""Explicit role-to-scope grant SQLAlchemy model."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Boolean, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import Base
from persistence.database.mixins import CreatedAtMixin


class RoleScopeGrantModel(CreatedAtMixin, Base):
    """Persist one exact role-to-scope grant without inheritance."""

    __tablename__ = "role_scope_grants"
    __table_args__ = (
        ForeignKeyConstraint(
            ("role_id",),
            ("authorization_roles.id",),
            name="fk_role_scope_grants_role_id_authorization_roles",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ("scope_id",),
            ("oauth_scopes.id",),
            name="fk_role_scope_grants_scope_id_oauth_scopes",
            ondelete="RESTRICT",
        ),
    )

    role_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )
    scope_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False)
