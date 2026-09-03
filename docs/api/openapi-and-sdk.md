# OpenAPI and SDK

`authService` publishes the unmodified FastAPI OpenAPI 3.1 document directly through
`GET /getOpenApi`.

## Publication

The path `/getOpenApi` and operation ID `getOpenApi` are stable code contracts rather than runtime
settings. Built-in `/openapi.json`, `/docs`, and `/redoc` routes are disabled.

The document contains ordinary paths, request schemas, response schemas, summaries, descriptions,
tags, and status responses. Protected routes contribute FastAPI's standard OAuth2
client-credentials security scheme and exact scope requirement. No vendor extension, custom route
metadata, scope map, or post-processing is used.

The current `/getToken` operation has no access-token security requirement. Its OpenAPI request body
is `PokerlostRequest[GetTokenRequest]`, and its SDK method declares `__scopes__ = None`.

Protected operations use `Security(authorize_pokerlost_request, scopes=[...])`. FastAPI publishes
the catalog under `components.securitySchemes.PokerlostOAuth2` and the exact non-empty list under
the operation's standard `security` field. authService currently has no implemented protected
route, so its production document honestly has no security requirement and may omit
`components.securitySchemes`. Neither the service nor generator adds a fake route, injected
component, extension, or scope map to force an otherwise-unused scheme into the document.

## Generation

The authoritative generator reads service documents, skips infrastructure routes, and validates
the POST/JSON/envelope/security contract and global name uniqueness. A document with no protected
operation needs no OAuth2 scheme, and its public methods receive `__scopes__ = None`. Once a
protected operation exists, its standard OpenAPI security requirement must contain a non-empty
scope list whose values already exist in the explicit shared `PokerlostScopes` SDK catalog. The
generator writes only the flat method/type modules owned by its manifest.

Manual future-facing method stubs remain outside the generator manifest unless explicitly owned.
They perform ordinary SDK calls when their endpoints exist and never return synthetic success.

## Calls

Inter-service calls use `PokerlostClient` and generated `PokerlostMethod` classes. Every call
serializes `PokerlostRequest`; protected calls pass through retry then authentication middleware,
which injects the bearer header internally. The complete lifecycle is in
`docs/architecture/inter-service-clients.md`.
