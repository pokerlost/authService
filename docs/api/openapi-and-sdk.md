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

The method generator reads `/oauth.token` as an ordinary operation. Standard OpenAPI
`requestBody.content` preserves its `application/x-www-form-urlencoded` request, the security
scheme preserves HTTP Basic, and the response schemas preserve the success and failure envelopes.
The generated `OAuthTokenMethod` reuses the shared SDK `OAuthTokenResponse` instead of generating
a duplicate model.

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

The SDK owns transport, generated methods, shared authorization models, generic request headers,
canonical exceptions, and `PokerLostRetryPolicy`; it does not own token acquisition, credentials,
token storage or caching, refresh, auth-specific middleware, or bearer injection. A consuming
service owns token orchestration through an application port and a focused adapter over the
generated `OAuthTokenMethod`. Generic per-call headers carry caller-supplied authorization, while
retry uses the canonical transport policy:

```python
from pypokerlost.client.request import RequestOptions
from pypokerlost.client.retry import PokerLostRetryPolicy
```

Token credentials, requested scopes, storage, caching and refresh decisions remain inside the
consuming service. Retry remains off without an explicit
`RequestOptions(retry=PokerLostRetryPolicy())`, and the SDK never automatically replays `401` or
`403`. The exact extension pattern is documented in
`docs/architecture/inter-service-clients.md`.

Business mutation replay remains the consumer's responsibility: it must reuse the same
`business_operation_id` and semantic payload and rely on the target's persisted idempotency
contract. A consumer must not hold a PostgreSQL transaction across token acquisition, an outbound
method call, or retry backoff. authService itself does not instantiate an outbound client to itself
or accountsService; token issuance, login-grant exchange, refresh, and JWT signing are local
service responsibilities.

The current endpoints and their publication models are listed in
`docs/api/public-surface.md`.
