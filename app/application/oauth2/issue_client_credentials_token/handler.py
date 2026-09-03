"""Service-client credential token issuance orchestration."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from pydantic import SecretStr
from pypokerlost.enums import PrincipalStatus, PrincipalType
from pypokerlost.types import PokerlostAccessTokenClaims

from application.oauth2 import (
    InvalidOAuthClientError,
    InvalidRequestedScopeError,
    InvalidTargetAudienceError,
    UnauthorizedOAuthClientError,
)
from application.ports import (
    ClientCredentialsAuthorizationContext,
    ClientCredentialsQuery,
    Handler,
    OAuthClientSecretProcessor,
    ServiceAccessTokenSigner,
)
from domain.enums import (
    OAuthClientStatus,
    OAuthClientType,
    OAuthGrantType,
)

from .command import IssueClientCredentialsTokenCommand
from .result import IssueClientCredentialsTokenResult


class IssueClientCredentialsTokenHandler(
    Handler[IssueClientCredentialsTokenCommand, IssueClientCredentialsTokenResult],
):
    """Authenticate one confidential service client and sign its exact grants."""

    __slots__ = (
        "_access_token_ttl_seconds",
        "_client_credentials_query",
        "_issuer",
        "_secret_processor",
        "_signer",
    )

    def __init__(
        self,
        client_credentials_query: ClientCredentialsQuery,
        secret_processor: OAuthClientSecretProcessor,
        signer: ServiceAccessTokenSigner,
        *,
        issuer: str,
        access_token_ttl_seconds: int,
    ) -> None:
        """Store exact policy and caller-owned authorization adapters."""
        if not issuer.strip() or issuer != issuer.strip():
            raise ValueError("Token issuer must be non-empty and have no outer whitespace")
        if not 60 <= access_token_ttl_seconds <= 3600:
            raise ValueError("Access-token TTL must be between 60 and 3600 seconds")
        self._client_credentials_query = client_credentials_query
        self._secret_processor = secret_processor
        self._signer = signer
        self._issuer = issuer
        self._access_token_ttl_seconds = access_token_ttl_seconds

    async def __call__(
        self,
        input_: IssueClientCredentialsTokenCommand,
        /,
    ) -> IssueClientCredentialsTokenResult:
        """Issue one fresh short-lived RS256 token after exact intersection checks."""
        context = await self._client_credentials_query.get_authorization_context(
            input_.client_id,
        )
        if context is None:
            raise InvalidOAuthClientError

        now = datetime.now(UTC)
        self._authenticate_client(context, input_.client_secret, at=now)
        principal_id = self._validate_service_binding(context)

        if OAuthGrantType.CLIENT_CREDENTIALS not in context.grant_types:
            raise UnauthorizedOAuthClientError

        requested_scopes = frozenset(input_.requested_scopes)
        if not requested_scopes or len(requested_scopes) != len(input_.requested_scopes):
            raise InvalidRequestedScopeError
        if not (
            requested_scopes.issubset(context.principal_scopes)
            and requested_scopes.issubset(context.client_scopes)
        ):
            raise InvalidRequestedScopeError
        if not (
            input_.audience in context.principal_audiences
            and input_.audience in context.client_audiences
        ):
            raise InvalidTargetAudienceError

        scopes = tuple(sorted(requested_scopes))
        expires_at = now + timedelta(seconds=self._access_token_ttl_seconds)
        token = self._signer.sign(
            PokerlostAccessTokenClaims(
                issuer=self._issuer,
                subject=principal_id,
                audience=input_.audience,
                issued_at=now,
                not_before=now,
                expires_at=expires_at,
                token_id=uuid4(),
                client_id=context.client_id,
                scopes=scopes,
                principal_type=PrincipalType.SERVICE,
            ),
        )
        return IssueClientCredentialsTokenResult(
            access_token=SecretStr(token),
            expires_in=self._access_token_ttl_seconds,
            scopes=scopes,
            audience=input_.audience,
        )

    def _authenticate_client(
        self,
        context: ClientCredentialsAuthorizationContext,
        secret: SecretStr,
        *,
        at: datetime,
    ) -> None:
        """Authenticate without disclosing client or credential failure details."""
        if context.client_status is not OAuthClientStatus.ACTIVE:
            raise InvalidOAuthClientError
        if context.client_type is not OAuthClientType.CONFIDENTIAL:
            raise InvalidOAuthClientError
        matches = tuple(
            self._secret_processor.verify(secret, credential.secret_digest)
            for credential in context.credentials
            if credential.accepts_at(at)
        )
        if not any(matches):
            raise InvalidOAuthClientError

    @staticmethod
    def _validate_service_binding(
        context: ClientCredentialsAuthorizationContext,
    ) -> UUID:
        """Require the exact active service principal bound to the client."""
        if (
            context.bound_principal_id is None
            or context.principal_id is None
            or context.bound_principal_id != context.principal_id
            or context.principal_type is not PrincipalType.SERVICE
            or context.principal_status is not PrincipalStatus.ACTIVE
        ):
            raise InvalidOAuthClientError
        return context.principal_id
