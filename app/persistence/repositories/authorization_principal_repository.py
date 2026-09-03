"""SQLAlchemy authorization principal repository adapter."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Never
from uuid import UUID

from pypokerlost.enums import PrincipalStatus, PrincipalType
from sqlalchemy import ColumnElement, select, update
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError

from application.errors import IntegrityError as ApplicationIntegrityError
from application.errors import PrincipalConflictError
from application.ports import AuthorizationPrincipalRepository
from domain.authorization_principal import AuthorizationPrincipal
from persistence.database.models import AuthorizationPrincipalModel

from .base import SQLAlchemyRepository

_PRINCIPAL_BINDING_CONSTRAINTS = frozenset(
    {
        "uq_authorization_principals_account_id",
        "uq_authorization_principals_service_slug",
    },
)


def _constraint_name(exception: SQLAlchemyIntegrityError) -> str | None:
    """Read a PostgreSQL constraint name without depending on a private driver type."""
    current: BaseException | None = exception.orig
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        name = getattr(current, "constraint_name", None)
        if isinstance(name, str):
            return name
        current = current.__cause__ or current.__context__
    return None


def _raise_application_integrity_error(exception: SQLAlchemyIntegrityError) -> Never:
    """Translate known binding uniqueness failures and sanitize every other violation."""
    if _constraint_name(exception) in _PRINCIPAL_BINDING_CONSTRAINTS:
        raise PrincipalConflictError from exception
    raise ApplicationIntegrityError from exception


class SQLAlchemyAuthorizationPrincipalRepository(
    SQLAlchemyRepository,
    AuthorizationPrincipalRepository,
):
    """Persist role-free principal aggregates in the request-owned transaction."""

    async def add(self, principal: AuthorizationPrincipal) -> None:
        """Add and flush one principal so named uniqueness failures are observable."""
        model = AuthorizationPrincipalModel(
            id=principal.principal_id,
            principal_type=principal.principal_type.value,
            status=principal.status.value,
            account_id=principal.account_id,
            service_slug=principal.service_slug,
            created_at=principal.created_at,
            updated_at=principal.updated_at,
        )
        self._session.add(model)
        try:
            await self._session.flush((model,))
        except SQLAlchemyIntegrityError as exception:
            _raise_application_integrity_error(exception)

    async def get_by_principal_id(
        self,
        principal_id: UUID,
    ) -> AuthorizationPrincipal | None:
        """Return the aggregate with the exact principal identifier."""
        return await self._get_principal((AuthorizationPrincipalModel.id == principal_id,))

    async def get_human_by_account_id(
        self,
        account_id: UUID,
    ) -> AuthorizationPrincipal | None:
        """Return the exact human account binding."""
        return await self._get_principal(
            (
                AuthorizationPrincipalModel.principal_type == PrincipalType.HUMAN.value,
                AuthorizationPrincipalModel.account_id == account_id,
            ),
        )

    async def get_service_by_service_slug(
        self,
        service_slug: str,
    ) -> AuthorizationPrincipal | None:
        """Return the exact internal service binding."""
        return await self._get_principal(
            (
                AuthorizationPrincipalModel.principal_type == PrincipalType.SERVICE.value,
                AuthorizationPrincipalModel.service_slug == service_slug,
            ),
        )

    async def save(self, principal: AuthorizationPrincipal) -> None:
        """Persist one validated aggregate mutation without completing its transaction."""
        statement = (
            update(AuthorizationPrincipalModel)
            .where(AuthorizationPrincipalModel.id == principal.principal_id)
            .values(
                principal_type=principal.principal_type.value,
                status=principal.status.value,
                account_id=principal.account_id,
                service_slug=principal.service_slug,
                updated_at=principal.updated_at,
            )
            .returning(AuthorizationPrincipalModel.id)
        )
        try:
            result = await self._session.execute(statement)
        except SQLAlchemyIntegrityError as exception:
            _raise_application_integrity_error(exception)
        if result.scalar_one_or_none() is None:
            raise ApplicationIntegrityError

    async def _get_principal(
        self,
        conditions: Sequence[ColumnElement[bool]],
    ) -> AuthorizationPrincipal | None:
        result = await self._read_scalar(
            select(AuthorizationPrincipalModel).where(*conditions),
        )
        model = result.one_or_none()
        if model is None:
            return None
        return AuthorizationPrincipal(
            principal_id=model.id,
            principal_type=PrincipalType(model.principal_type),
            status=PrincipalStatus(model.status),
            account_id=model.account_id,
            service_slug=model.service_slug,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
