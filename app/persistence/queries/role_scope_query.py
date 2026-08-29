"""SQLAlchemy role and explicit scope-grant query adapter."""

from __future__ import annotations

from collections.abc import Collection

from sqlalchemy import select

from application.errors import RoleNotFoundError, ScopeNotFoundError
from application.ports import RoleScopeQuery
from domain.authorization_role import AuthorizationRole
from domain.enums import PrincipalType, RoleCode
from domain.oauth_scope import OAuthScope
from domain.scope_name import ScopeName
from persistence.database.models import (
    AuthorizationRoleModel,
    OAuthScopeModel,
    RoleScopeGrantModel,
)
from persistence.repositories import SQLAlchemyRepository


class SQLAlchemyRoleScopeQuery(SQLAlchemyRepository, RoleScopeQuery):
    """Read exact persisted roles, scopes, and explicit grants."""

    async def get_role_by_code(self, code: RoleCode) -> AuthorizationRole:
        """Return one persisted role by its exact stable code."""
        model = await self._get_role_model(code)
        return AuthorizationRole(
            role_id=model.id,
            code=RoleCode(model.code),
            principal_type=PrincipalType(model.principal_type),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_scopes_by_exact_names(
        self,
        names: Collection[ScopeName],
    ) -> tuple[OAuthScope, ...]:
        """Return the exact requested catalog scopes or fail closed when one is absent."""
        requested_names = frozenset(name.value for name in names)
        if not requested_names:
            return ()
        result = await self._read_scalar(
            select(OAuthScopeModel)
            .where(OAuthScopeModel.name.in_(requested_names))
            .order_by(OAuthScopeModel.name),
        )
        models = result.all()
        if {model.name for model in models} != requested_names:
            raise ScopeNotFoundError
        return tuple(self._scope_from_model(model) for model in models)

    async def resolve_allowed_scope_names(self, role: RoleCode) -> frozenset[ScopeName]:
        """Resolve all explicit grant rows for the exact persisted role."""
        return await self._resolve_scope_names(role, default_only=False)

    async def resolve_default_scope_names(self, role: RoleCode) -> frozenset[ScopeName]:
        """Resolve only explicit default grant rows for the exact persisted role."""
        return await self._resolve_scope_names(role, default_only=True)

    async def _get_role_model(self, code: RoleCode) -> AuthorizationRoleModel:
        result = await self._read_scalar(
            select(AuthorizationRoleModel).where(AuthorizationRoleModel.code == code.value),
        )
        model = result.one_or_none()
        if model is None:
            raise RoleNotFoundError
        return model

    async def _resolve_scope_names(
        self,
        role: RoleCode,
        *,
        default_only: bool,
    ) -> frozenset[ScopeName]:
        role_model = await self._get_role_model(role)
        statement = (
            select(OAuthScopeModel.name)
            .join(
                RoleScopeGrantModel,
                RoleScopeGrantModel.scope_id == OAuthScopeModel.id,
            )
            .where(RoleScopeGrantModel.role_id == role_model.id)
        )
        if default_only:
            statement = statement.where(RoleScopeGrantModel.is_default.is_(True))
        result = await self._read_scalar(statement)
        return frozenset(ScopeName.parse(name) for name in result.all())

    @staticmethod
    def _scope_from_model(model: OAuthScopeModel) -> OAuthScope:
        return OAuthScope(
            scope_id=model.id,
            name=ScopeName.parse(model.name),
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
