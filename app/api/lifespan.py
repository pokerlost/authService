"""Application runtime resource lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from fastapi import FastAPI

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
from configuration import Settings
from observability import instrument_database
from persistence.database import create_database_engine, create_session_factory

from .resources import ApplicationResources


def create_lifespan(
    settings: Settings,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None, bool | None]]:
    """Create runtime database and signing resources during application startup."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        engine = create_database_engine(
            settings.database,
            application_name=settings.application.service_name,
        )
        signing_key_provider = SigningKeyProvider(settings.jwt)
        password_hasher = Argon2PasswordHasher(
            time_cost=settings.password.time_cost,
            memory_cost_kib=settings.password.memory_cost_kib,
            parallelism=settings.password.parallelism,
            hash_length=settings.password.hash_length,
            salt_length=settings.password.salt_length,
        )
        refresh_token_protector = RefreshTokenProtector(settings.refresh_token.pepper)
        service_credential_protector = ServiceCredentialProtector(
            settings.service_auth.credential_pepper,
        )
        oauth_scope_parser = OAuthScopeParser(
            max_scope_count=settings.oauth2.max_requested_scopes,
            max_scope_token_length=settings.oauth2.max_scope_token_length,
            max_total_bytes=settings.oauth2.max_total_scope_claim_bytes,
        )
        access_token_issuer = AccessTokenIssuer(
            issuer=settings.jwt.issuer,
            audience=settings.jwt.human_audience,
            ttl_seconds=settings.jwt.access_token_ttl_seconds,
            signing_key_provider=signing_key_provider,
            scope_parser=oauth_scope_parser,
            max_access_token_bytes=settings.oauth2.max_access_token_bytes,
        )
        access_token_verifier = AccessTokenVerifier(
            issuer=settings.jwt.issuer,
            audience=settings.jwt.human_audience,
            leeway=settings.jwt.clock_skew,
            signing_key_provider=signing_key_provider,
            scope_parser=oauth_scope_parser,
        )
        machine_access_token_issuer = MachineAccessTokenIssuer(
            issuer=settings.jwt.issuer,
            ttl_seconds=settings.service_auth.access_token_ttl_seconds,
            signing_key_provider=signing_key_provider,
            scope_parser=oauth_scope_parser,
            max_access_token_bytes=settings.oauth2.max_access_token_bytes,
        )
        try:
            instrument_database(engine, settings)
            resources = ApplicationResources(
                engine=engine,
                session_factory=create_session_factory(engine),
                signing_key_provider=signing_key_provider,
                password_hasher=password_hasher,
                refresh_token_protector=refresh_token_protector,
                access_token_issuer=access_token_issuer,
                access_token_verifier=access_token_verifier,
                service_credential_protector=service_credential_protector,
                machine_access_token_issuer=machine_access_token_issuer,
                oauth_scope_parser=oauth_scope_parser,
            )
            application.state.resources = resources
            application.state.settings = settings
            yield
        finally:
            application.state.resources = None
            application.state.settings = None
            await engine.dispose()

    return lifespan
