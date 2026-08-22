"""Standard UUID ORM entity base."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database.base import Base


class UUIDModel(Base):
    """Abstract entity with a Python-generated UUID primary key."""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
