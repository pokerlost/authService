# authService

SERVICE_NAME: authService
SERVICE_SLUG: authservice

## Purpose

Pokerlost token authority and authorization-state owner.

The public wire contract is the Pokerlost JSON protocol over HTTPS. Protected operations use a
standard OAuth2 bearer header while business-operation successes and handled failures use
`PokerlostResponse` JSON. `GET /getOpenApi` publishes the raw generated OpenAPI document.

## Responsibilities

- Own authorization principals and principal types.
- Own authorization clients, exact scope definitions, direct principal/client scope grants, and
  direct principal/client audience grants.
- Own one-time login grants as a future business stage.
- Issue short-lived service access tokens from body-supplied client credentials.
- Own future human sessions, refresh-token families and revocation state.
- Own service credentials and JWT signing metadata; JWKS publication is deferred.
- Provide future idempotent authorization-state operations used by accountsService.

## Service-specific rules

- `public` means an operation has no access-token scope requirement; it is not a principal,
  persisted classification, scope, or claim.
- Human and service principals receive authority only through explicit direct scope grants.
- Password hashes, password verification, usernames, nicknames and account lifecycle belong to
  accountsService.
- Runtime authorization uses exact Pokerlost scopes and never wildcard or identity-category
  bypasses.
- Downstream services validate short-lived JWT access tokens locally and do not call authService
  for each protected request.
- Pokerlost inter-service calls use `pypokerlost`; no direct HTTP fallback is allowed.
- authService does not instantiate a client to itself or accountsService.
- Existing applied migrations are immutable; persisted scope spelling changes use forward
  migrations.

## Current service-client profile

- `authservice bootstrap-service-client` is the operator bootstrap boundary.
- Bootstrap creates one active service principal, one bound confidential client, exact principal
  and client scope grants, exact principal and client audience grants, and one digest-only
  credential.
- `POST /getToken` is the only implemented business operation.
- Its request is `PokerlostRequest[GetTokenRequest]` JSON with `client_id`, `client_secret`, exact
  `scopes`, and logical service `audience` inside `payload`.
- Client credentials for this public access-token operation are accepted only in its typed JSON
  payload. They are not access-token authorization metadata.
- The audience is one exact service name such as `authService` or `accountsService` in the request,
  persisted grants, response, and JWT `aud` claim.
- FastAPI validates and serializes the route's plain success mapping as the
  `PokerlostResponse[PokerlostToken]` wire body; failures use `PokerlostResponse[None]`. Retry
  delay, when applicable, is represented only by `PokerlostResponse.retry_after`.
- A service token is short-lived, contains service-only claims, and is not persisted.
- The current flow creates no human session or refresh token.

## Operation identifiers

- Operation identifiers match `^[a-z][A-Za-z0-9]*$` and paths are `/<operationId>`.
- Current business operation: `getToken` at `POST /getToken`.
- Reserved future SDK operations are `refreshToken`, `getJwks`, `provisionHuman`,
  `setPrincipalStatus`, `replacePrincipalScopes`, and `issueLoginGrant`; they are not current
  server endpoints.
- Scope identifiers remain separate dotted lowerCamelCase values, for example
  `auth.internal.provisionHuman` and `auth.internal.replacePrincipalScopes`.

## Non-goals of the current stage

Human login-grant exchange, refresh tokens, sessions, logout, JWKS publication, principal HTTP
operations, retained signing keys, and signing-key rotation are not implemented.
