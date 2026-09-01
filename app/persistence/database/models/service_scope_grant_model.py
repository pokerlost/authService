"""Direct service-principal scope grant SQLAlchemy model."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import Base
from persistence.database.mixins import CreatedAtMixin


class ServiceScopeGrantModel(CreatedAtMixin, Base):
    """Persist one exact direct service-principal OAuth2 scope grant."""

    __tablename__ = "service_scope_grants"
    __table_args__ = (
        ForeignKeyConstraint(
            ("principal_id",),
            ("authorization_principals.id",),
            name="fk_service_scope_grants_principal_id_authorization_principals",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ("scope_id",),
            ("oauth_scopes.id",),
            name="fk_service_scope_grants_scope_id_oauth_scopes",
            ondelete="RESTRICT",
        ),
    )

    principal_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )
    scope_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )
