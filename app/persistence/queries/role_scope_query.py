"""SQLAlchemy role and explicit scope-grant query adapter."""

from __future__ import annotations

from collections.abc import Collection

from pypokerlost.contracts.authorization import AuthorizationRole, PrincipalType
from pypokerlost.types import OAuthScope, parse_oauth_scope_string
from sqlalchemy import select

from application.errors import RoleNotFoundError, ScopeNotFoundError
from application.ports import RoleScopeQuery
from domain.authorization_role_definition import AuthorizationRoleDefinition
from domain.oauth_scope_definition import OAuthScopeDefinition
from persistence.database.models import (
    AuthorizationRoleModel,
    OAuthScopeModel,
    RoleScopeGrantModel,
)
from persistence.repositories import SQLAlchemyRepository


class SQLAlchemyRoleScopeQuery(SQLAlchemyRepository, RoleScopeQuery):
    """Read exact persisted roles, scopes, and explicit grants."""

    async def get_role_by_code(self, code: AuthorizationRole) -> AuthorizationRoleDefinition:
        """Return one persisted role by its exact stable code."""
        model = await self._get_role_model(code)
        return AuthorizationRoleDefinition(
            role_id=model.id,
            code=AuthorizationRole(model.code),
            principal_type=PrincipalType(model.principal_type),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_scopes_by_exact_names(
        self,
        names: Collection[OAuthScope],
    ) -> tuple[OAuthScopeDefinition, ...]:
        """Return the exact requested catalog scopes or fail closed when one is absent."""
        requested_names = frozenset(names)
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

    async def resolve_allowed_scope_names(
        self,
        role: AuthorizationRole,
    ) -> frozenset[OAuthScope]:
        """Resolve all explicit grant rows for the exact persisted role."""
        return await self._resolve_scope_names(role, default_only=False)

    async def resolve_default_scope_names(
        self,
        role: AuthorizationRole,
    ) -> frozenset[OAuthScope]:
        """Resolve only explicit default grant rows for the exact persisted role."""
        return await self._resolve_scope_names(role, default_only=True)

    async def _get_role_model(self, code: AuthorizationRole) -> AuthorizationRoleModel:
        result = await self._read_scalar(
            select(AuthorizationRoleModel).where(AuthorizationRoleModel.code == code.value),
        )
        model = result.one_or_none()
        if model is None:
            raise RoleNotFoundError
        return model

    async def _resolve_scope_names(
        self,
        role: AuthorizationRole,
        *,
        default_only: bool,
    ) -> frozenset[OAuthScope]:
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
        names = result.all()
        if not names:
            return frozenset()
        return frozenset(parse_oauth_scope_string(" ".join(names)))

    @staticmethod
    def _scope_from_model(model: OAuthScopeModel) -> OAuthScopeDefinition:
        (name,) = parse_oauth_scope_string(model.name)
        return OAuthScopeDefinition(
            scope_id=model.id,
            name=name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
