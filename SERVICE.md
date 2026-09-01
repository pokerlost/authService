# authService

SERVICE_NAME: authService
SERVICE_SLUG: authservice

## Purpose

OAuth2 authorization server and token authority for PokerLost.

## Responsibilities

- Own authorization principals and principal types.
- Own OAuth2 clients, roles, scopes, role grants, direct service grants and audience grants.
- Own one-time login grants.
- Issue service access tokens; human access and refresh-token flows remain later responsibilities.
- Own human sessions, refresh-token families and revocation state.
- Own service credentials and JWT signing metadata; JWKS publication is deferred.
- Provide idempotent authorization-state operations used by accountsService.

## Service-specific rules

- Canonical access categories are `public`, `user`, `support`, `master` and `auto`.
- `public` means unauthenticated access; it is not a persisted role, principal, scope or token claim.
- Human principals use exactly `user`, `support` or `master`.
- Service principals use exactly `auto`.
- Password hashes, Argon2id policy, password verification, usernames, nicknames and account lifecycle belong to accountsService.
- Runtime authorization uses explicit OAuth2 scopes, never role checks.
- Roles have no implicit inheritance; each role owns a complete explicit scope bundle.
- `master` is not a global bypass.
- `auto` does not imply access to every internal operation; service access requires direct scope and audience grants.
- Protected FastAPI operations declare scopes through `Security(..., scopes=[...])`.
- PokerLost inter-service calls use generated `pypokerlost` clients and response types; no direct HTTP fallback is allowed.
- Downstream services validate short-lived JWT access tokens locally and do not call authService per request.
- `/oauth.token` preserves OAuth2 form and HTTP Basic request mechanics, while every success and
  handled failure uses the universal PokerLost `ApplicationResponse` envelope.
- Service principals use `client_credentials`, receive no human session and receive no refresh token.
- Service-client authentication uses HTTP Basic only; body `client_id` and `client_secret` fields are rejected.
- The resource indicator is exactly `urn:pokerlost:service:<serviceIdentity>` and becomes the
  unchanged JWT `aud` value.
- Requested service scopes and resources must be granted independently to both the service
  principal and its exact bound OAuth client.
- Generated OAuth client secrets are stored only as dedicated domain-separated SHA-256 digests
  and are shown once by the operator bootstrap command.
- JWT signing uses RS256 with mandatory `kid`; the private key is loaded from a mounted Secret file.
- AUTH-02 publishes no JWKS and retains no signing-key history; those capabilities remain deferred.
- Service consumers acquire credentials through `ClientCredentialsTokenProvider`, add bearer
  authentication through `BearerTokenMiddleware`, and register `RetryMiddleware` outside bearer
  middleware. Retry remains disabled without an explicit per-call policy and never replays `401`
  or `403` automatically.
- These are consumer-side SDK concerns. authService does not instantiate an outbound client to
  itself or to accountsService during token issuance, refresh, or credential validation.

## Current service-client profile

- `authservice bootstrap-service-client` is the only client bootstrap boundary.
- The bootstrap transaction creates one active `service` principal with role `auto`, one active
  confidential client bound to it, explicit `client_credentials` permission, matching direct and
  client scope grants, matching service and client audience grants, and one active secret digest.
- `POST /oauth.token` executes only `grant_type=client_credentials`.
- The request is `application/x-www-form-urlencoded` with exactly one `grant_type`, `scope`, and
  `resource`, plus an HTTP Basic `Authorization` header.
- Success returns `ApplicationResponse[OAuthTokenResponse]`; handled failure returns
  `ApplicationResponse[None]`. The access token exists only at `result.access_token`.
- A service token is short-lived, contains service-only claims, uses the exact requested resource
  as `aud`, and is not persisted.
- The flow does not create a session, refresh token, account claim, or role-derived scope grant.

## Operation identifiers

- PokerLost operation identifiers use `namespace.someOperation`, where both the stable namespace and operation use lowerCamelCase.
- Operation paths are exactly the operation identifier prefixed with `/`.
- Reserved identifiers for later authorization responsibilities are `principals.provisionHuman`,
  `principals.setStatus`, `principals.assignRole`, and `loginGrants.issue`; they are not part of the
  current HTTP surface.
- OAuth2 scope identifiers are separate lowercase dotted values and retain names such as `auth.internal.provision_human`.

## Protocol vocabulary

- Human login grant: `urn:pokerlost:params:oauth:grant-type:login-grant`.
- Refresh: `refresh_token`.
- Service authentication: `client_credentials`, the only executable grant in the current service.
- Human login-grant exchange, refresh, password, implicit, device, OIDC and social-login grants
  are not implemented.
