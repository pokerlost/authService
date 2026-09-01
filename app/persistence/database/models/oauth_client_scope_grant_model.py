"""Direct OAuth2 client scope grant SQLAlchemy model."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database import Base
from persistence.database.mixins import CreatedAtMixin


class OAuthClientScopeGrantModel(CreatedAtMixin, Base):
    """Persist one exact direct OAuth2 client scope grant."""

    __tablename__ = "oauth_client_scope_grants"
    __table_args__ = (
        ForeignKeyConstraint(
            ("client_id",),
            ("oauth_clients.id",),
            name="fk_oauth_client_scope_grants_client_id_oauth_clients",
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ("scope_id",),
            ("oauth_scopes.id",),
            name="fk_oauth_client_scope_grants_scope_id_oauth_scopes",
            ondelete="RESTRICT",
        ),
    )

    client_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )
    scope_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
    )
