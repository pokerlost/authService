# authService

The current checkout is a template-derived foundation with only infrastructure routes. Token
issuance, operator bootstrap, and authorization persistence are planned in `SERVICE.md`, not active
runtime behavior. The installed package lives under `src/authService/`. Historical Alembic
revisions are retained byte-for-byte under `migrations/versions/` and must not be rewritten.
`PROJECT.md`, `SERVICE.md`, settings, scopes, service code, and revisions are project-owned.
This stage adds no product endpoints, fake verifier, new test dependencies, CI, or checker scripts.

Before every task:

1. Read `AGENTS.md` and `SERVICE.md`.
2. Inspect the current repository and relevant implementation.
3. Treat the latest direct user requirement as highest priority.
4. Preserve service-owned behavior, migrations, and local changes.

Priority:

```text
latest direct user requirement
→ SERVICE.md
→ AGENTS.md
→ current implementation
→ older decisions
```

## General architecture

- Keep API, application, domain, configuration, observability, persistence, and CLI
  responsibilities separated.
- Do not introduce an abstraction without a concrete responsibility.
- PostgreSQL remains the primary persistence layer.
- Validate critical settings at startup and fail closed.
- Do not commit or log secrets.
- New project-owned private files, variables, and functions use lowerCamelCase; types use PascalCase
  and constants use UPPER_SNAKE_CASE. Preserve generated paths, framework hooks, published imports,
  wire/SQL fields, environment names, and override signatures.

## Pokerlost JSON protocol

- Pokerlost service calls use JSON over HTTPS. Protected business operations receive one access
  token only as `Authorization: Bearer <access-token>`; public operations send no access token.
- `GET /`, `GET /getOpenApi`, and existing health probes are the only public infrastructure
  exceptions. They accept no business body or authentication material.
- Every business/API operation uses `POST /<operationId>` with one JSON request body and one JSON
  `PokerlostResponse` body.
- Every operation ID matches `^[a-z][A-Za-z0-9]*$`. Use a single lowerCamelCase verb name such as
  `getMe`, `registerAccount`, or `provisionHuman`.
- Do not use business path parameters, query parameters, cookies, caller-supplied transport
  metadata, GET bodies, form data, content negotiation, or manual content-type construction.
- Every operation accepts the pure JSON `PokerlostRequest[Payload]` envelope. Request bodies never
  contain an access token, headers map, method binding, or middleware state.
- Client credentials belong only in the `getToken` JSON payload. A refresh token belongs only in
  the `refreshToken` JSON payload. Do not prepend a token type string.
- Every `src/authService/routers/<operation>.py` module owns one module-level
  `router = APIRouter(...)`, and its decorated endpoints are module-level functions. Static router
  factories, nested endpoints, one-directory-per-router layouts, route constants used once,
  imperative registration, and post-hoc route mutation are forbidden.
- Pydantic request models parse and validate UUIDs, enums, credentials, audiences, and other wire
  values. Route modules do not define `_parse_*` or `_validate_*` helpers for primitive input.

## Responses and errors

- Every normal endpoint declares `pypokerlost.types.PokerlostResponse[ResultT]` as its
  `response_model` and returns plain Python mappings or data. FastAPI owns success validation and
  serialization into exactly `ok`, `result`, `error`, `error_message`, and `retry_after`.
- Application handlers return focused application results and do not import or return FastAPI,
  HTTP response types, status codes, or `PokerlostResponse`.
- Only centralized exception/error code manually constructs `PokerlostResponse[None]` before
  serializing it through `JSONResponse`; normal endpoints do neither.
- Success requires null error metadata and null `retry_after`. Failure requires a stable error
  code, null result, an optional safe message, and an optional finite non-negative retry delay.
- Do not create a parallel service response envelope or an application-layer Result wrapper with
  the same wire shape.
- Central handlers return sanitized failures and never echo request input, response bodies,
  tracebacks, SQL details, credentials, or tokens.
- Use Pydantic validation, `ValueError`/`TypeError`, application errors, or focused Pokerlost SDK
  errors. Project-owned runtime Python must not use assertions for validation or protocol state.

## Header authorization and scopes

- Pokerlost scopes use dot-separated lowerCamelCase segments and match
  `^[a-z][A-Za-z0-9]*(\.[a-z][A-Za-z0-9]*)+$`. Wildcards and identity-category bypasses are
  forbidden.
- Keep exactly one service-owned `Scopes(StrEnum)` catalog in `src/authService/scopes.py`; its
  focused description mapping is the source for standard OpenAPI OAuth2 metadata.
- SDK-owned shared wire enums live only in `pypokerlost/enums/`; API adapters map them to local
  domain enums when both representations are required.
- A protected route declares every exact scope through
  `Security(authorize_pokerlost_request, scopes=[...])`. A public route has no security dependency.
- `PokerlostTokenVerifier` is the transport-independent application port for local verification.
  A concrete service supplies a real verifier at composition only when its implemented stage
  protects a route. The template does not provide a fake verifier or remote verification call.
- The dependency uses FastAPI's standard OAuth2 scheme with `auto_error=False`, parses one bearer
  header, verifies locally for exact `SERVICE_NAME`, compares the returned audience, and requires
  every exact route scope before handler execution.
- Missing or malformed authentication fails with `POKERLOST_AUTHENTICATION_REQUIRED`; an invalid
  token or audience fails with `POKERLOST_ACCESS_TOKEN_INVALID`; expiry fails with
  `POKERLOST_ACCESS_TOKEN_EXPIRED`; missing scope fails with `POKERLOST_INSUFFICIENT_SCOPE`.
- Authorization is based only on direct exact scope grants. Do not call authService for every
  protected request.
- Authorization uses scopes only. Do not introduce authorization roles, role claims, role grants,
  role inheritance, or role checks; human and service are identity categories, not roles.
- Protected composition without a configured verifier must fail closed.

## OpenAPI

- Use FastAPI's standard OAuth2 client-credentials OpenAPI model without project-owned extensions,
  vendor metadata, route mutation, or post-processing.
- A protected route publishes exactly one `PokerlostOAuth2` requirement with one or more exact
  scopes. No security requirement means the generated method declares `__scopes__ = None`; an
  empty OAuth2 scope list is invalid.
- A document with no protected operations may omit `components.securitySchemes`; generation must
  accept it without fake routes, injected components, `openapi_extra`, custom `x-*` metadata, or a
  handwritten scope map.
- Keep built-in `/openapi.json`, `/docs`, and `/redoc` disabled. Publish the unmodified document
  through `GET /getOpenApi`.

## Pokerlost SDK compatibility

- The current `pypokerlost` public facade and generator are authoritative. Use flat public imports
  and do not import private modules, generator internals, or removed compatibility paths.
- Inter-service calls use `PokerlostClient` and generated `PokerlostMethod` classes. Do not add a
  parallel `httpx`, `requests`, or `aiohttp` transport, URL builder, decoder, or remote DTO copy.
- A concrete service creates one target-specific client only for a real dependency declared by
  `SERVICE.md`, owns it in lifespan, stores it in a named `ApplicationResources` field, and closes
  it on shutdown. The pristine service creates no outbound client.
- Protected outbound clients compose middleware in this order:

```text
PokerlostRetryMiddleware
→ PokerlostAuthenticationMiddleware
→ transport
```

- Authentication middleware loads shared token state for a protected method and injects only the
  bearer header. It never owns client credentials or initial `getToken` acquisition.
- A service-owned refresher may recover once only from exact
  `POKERLOST_ACCESS_TOKEN_EXPIRED`, then replay once. Local expiration metadata, invalid-token, and
  insufficient-scope failures never trigger refresh.
- Every concrete SDK method explicitly declares `__scopes__`. `None` means no access token and
  bypasses token state; a protected method uses a non-empty tuple. Empty or missing metadata is an
  error before network I/O.
- Retry remains disabled unless a call passes
  `PokerlostRequestOptions(retry_policy=PokerlostRetryPolicy())`. Do not expose retry algorithm
  settings through deployment configuration.
- The retry policy receives server guidance only from `PokerlostResponse.retry_after`. It never
  reads transport metadata.
- Token state uses an aware UTC `expires_at`, positive version, compare-and-swap persistence, and
  cross-process refresh coordination. Never persist monotonic time or rely on local lock maps.
- Transport retry is not business idempotency. A replayable mutation must reuse the same
  `business_operation_id`, semantic payload, operation, and target. Middleware never creates or
  changes business IDs or workflow persistence.
- Never keep a PostgreSQL transaction open during token acquisition, an outbound call, retry
  sleep, or another attempt.

## Sensitive data and observability

- Secret-bearing models must use `hide_input_in_errors=True` and repr-hidden fields.
- Never capture or log request/response bodies containing `client_secret`, `access_token`,
  `refresh_token`, passwords, login grants, or private keys.
- Keep FastAPI instrumentation body capture disabled and HTTP client debug logging disabled.
- Generate request IDs only on the server. Do not read or return request-correlation transport
  metadata as a public contract.

## Configuration and deployment

- Root and OpenAPI operation IDs are stable code contracts: `getRoot` and `getOpenApi`. They are
  not settings, environment variables, or Helm values.
- Put deployment policy in typed settings. Keep protocol invariants and business operation IDs in
  code.
- Production deployment requires HTTPS/TLS. The generated ClusterIP is an internal target and
  must remain behind trusted TLS termination; do not expose it as a plaintext production API.
- Secrets use environment injection or Kubernetes Secret references, never chart values or
  ConfigMaps.

## Application, domain, and persistence

- Application values and ports remain transport-independent. Ports do not expose FastAPI,
  SQLAlchemy sessions, or concrete SDK clients.
- Introduce application values and ports only for implemented behavior; do not populate an empty
  foundation with placeholder command or repository layers.
- Routes translate API schemas to application values; public models do not double as domain or ORM
  models.
- Service-owned scopes live in `src/authService/scopes.py`; do not create transport or persistence
  duplicates.
- A request-owned SQLAlchemy session owns one transaction. Routes, handlers, repositories, and
  query adapters do not commit or roll back directly.
- Keep repositories focused. When a service needs read projections, keep them separate from ORM
  entities and API responses rather than adding a generic projection framework to the foundation.
- Do not add a fake model or migration to a pristine service.

## Documentation and tooling

- Keep `README.md` as the landing page and `docs/index.md` as the documentation home.
- Write documentation in English with one H1, verified relative links to related files,
  language-tagged fences, and restrained emoji in navigation headings.
- Update `docs/api/public-surface.md` for every implemented operation. Wire changes also update the
  response, authorization, operation, and OpenAPI pages.
- Use the repository `Makefile`, `uv`, Ruff, mypy, Alembic, Docker, and Helm conventions.
- Do not add tests unless the user explicitly requests them. Do not add rendered-template tests,
  `scripts/check_*.py`, architecture checker scripts, or hidden equivalents.
- Before handoff, run the available non-test format, lint, type, documentation, compile, migration,
  and packaging checks individually, and report every unavailable or failed check.
