# OpenAPI and SDK

This page defines how `authService` publishes its FastAPI contract and how that contract is
consumed by the authoritative `pypokerlost` tooling.

## Publication endpoint

`Settings.openapi_operation` supplies both the publication `operation_id` and its
`"/" + operation_id` path. The `.env.example` value is `openapi.get`, so its example path is
`GET /openapi.get`. The operation accepts no parameters or request body and returns the OpenAPI
JSON object as the `result` of `OpenAPIResponse`. `OpenAPIResponse` is an
`ApplicationResponse` specialization, so publication uses the same success and failure invariants
as every other operation.

FastAPI's built-in `/openapi.json`, `/docs`, and `/redoc` routes are disabled. The application calls
FastAPI's `get_openapi()` for its registered routes, caches the resulting OpenAPI 3.1 document, and
adds exactly this required platform extension:

```yaml
x-pokerlost-service:
  id: authService
```

The identifier is the canonical Copier service identity, while API operation namespaces follow the
separate rules in `docs/api/operation-contract.md`. `info.version` comes from the
`application.version` setting and remains a semantic version.

Concrete security declarations come from the concrete service's FastAPI dependencies. The wrapper
preserves FastAPI-generated security metadata without constructing or rewriting it.

## Method generation

The authoritative generator reads the wrapped publication, ignores the two system paths, and
creates typed `PokerlostMethod` and response classes for compatible PokerLost application
operations.

The method generator sees `/oauth.token`, but its form request is intentionally outside ordinary
generated JSON operation input. The service keeps the accurate FastAPI-generated form, HTTP Basic,
success-envelope, and failure-envelope contract visible instead of hiding or rewriting it. The SDK
owns one focused internal token request in `ClientCredentialsTokenProvider`; that path reuses the
canonical session transport and `ApplicationResponse` decoder rather than creating a generated
business method or a consumer-owned HTTP client.

Generation is repository-owned development tooling in the authoritative `pypokerlost` checkout;
it is not an installed command in the runtime SDK distribution. Service mode receives the
publication operation explicitly through `--openapi-operation`; its default remains `openapi.get`.
When an application-operation wire contract changes, run the compatibility workflow against the
current SDK source and verify both service-mode and saved-file generation. The exact operation,
request, response, and supported-schema requirements are documented in
`docs/api/operation-contract.md` and `docs/api/application-response.md`.

## Inter-service calls

PokerLost services call one another only through `pypokerlost.Client` and generated methods and
response types. A concrete service creates a client only for a target declared by its
`SERVICE.md`, owns that client in application lifespan, reuses it across requests, and closes it on
shutdown. It does not create a parallel HTTP client, URL builder, response decoder, or local copy
of a remote service DTO.

A service consumer imports authentication and middleware from the focused public facades:

```python
from pypokerlost.client.auth import ClientCredentials, ClientCredentialsTokenProvider
from pypokerlost.middleware import BearerTokenMiddleware, RetryMiddleware
```

The target client registers `RetryMiddleware()` first and
`BearerTokenMiddleware(token_provider)` second. The first middleware is outermost, so every retry
attempt re-enters bearer resolution while the provider normally serves its process-local cached
token. Retry remains off without an explicit per-call `RequestOptions(retry=RetryPolicy(...))`, and
the SDK never automatically replays `401` or `403`.

Business mutation replay remains the consumer's responsibility: it must reuse the same
`business_operation_id` and semantic payload and rely on the target's persisted idempotency
contract. A consumer must not hold a PostgreSQL transaction across token acquisition, an outbound
method call, or retry backoff. authService itself does not instantiate an outbound client to itself
or accountsService; token issuance, login-grant exchange, refresh, and JWT signing are local
service responsibilities.

The current endpoints and their publication models are listed in
`docs/api/public-surface.md`.
