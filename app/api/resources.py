"""Runtime resources owned by the application lifespan."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from application.security import (
    AccessTokenIssuer,
    AccessTokenVerifier,
    Argon2PasswordHasher,
    MachineAccessTokenIssuer,
    OAuthScopeParser,
    RefreshTokenProtector,
    ServiceCredentialProtector,
    SigningKeyProvider,
)


class ApplicationResources:
    """Application runtime objects shared by request dependencies."""

    __slots__ = (
        "access_token_issuer",
        "access_token_verifier",
        "engine",
        "machine_access_token_issuer",
        "oauth_scope_parser",
        "password_hasher",
        "refresh_token_protector",
        "service_credential_protector",
        "session_factory",
        "signing_key_provider",
    )

    def __init__(
        self,
        *,
        engine: AsyncEngine,
        session_factory: async_sessionmaker[AsyncSession],
        signing_key_provider: SigningKeyProvider,
        password_hasher: Argon2PasswordHasher,
        refresh_token_protector: RefreshTokenProtector,
        access_token_issuer: AccessTokenIssuer,
        access_token_verifier: AccessTokenVerifier,
        service_credential_protector: ServiceCredentialProtector,
        machine_access_token_issuer: MachineAccessTokenIssuer,
        oauth_scope_parser: OAuthScopeParser,
    ) -> None:
        self.engine = engine
        self.session_factory = session_factory
        self.signing_key_provider = signing_key_provider
        self.password_hasher = password_hasher
        self.refresh_token_protector = refresh_token_protector
        self.access_token_issuer = access_token_issuer
        self.access_token_verifier = access_token_verifier
        self.service_credential_protector = service_credential_protector
        self.machine_access_token_issuer = machine_access_token_issuer
        self.oauth_scope_parser = oauth_scope_parser
