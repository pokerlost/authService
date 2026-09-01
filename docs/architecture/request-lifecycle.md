# Request lifecycle

This page traces startup, request context, dependency resolution, application execution, and safe
response handling in the generated service.

## Composition and lifespan

`create_app()` resolves `Settings`, configures observability, constructs the FastAPI application,
and registers request-context middleware, exception handlers, routes, and instrumentation. It
disables the built-in OpenAPI and documentation URLs.

Application lifespan creates the async SQLAlchemy engine, session factory, one process-owned
`BusinessOperationFingerprinter`, and one process-owned RS256 service-token signer. It instruments
the engine when configured and stores the resources in immutable `ApplicationResources`. Signer
construction reads and validates the configured PEM private key once, before requests are served.
Settings and resources are attached to application state for dependencies. Shutdown removes that
state and disposes the engine.

A concrete service with a real outbound target extends this same lifespan rather than adding a
second resource framework. It creates and starts one target-specific `pypokerlost.Client` before
publishing `ApplicationResources`, stores it in an explicitly named typed field, reuses it across
requests, and stops it in reverse ownership order. Partial startup failure unwinds resources that
already started. authService has no outbound target and therefore creates no outbound client,
token-acquisition port, token store or cache, target settings, or service-specific retry settings.

Creating the engine does not itself prove a PostgreSQL connection. A route opens a request session
only when it declares the database dependency; the root and OpenAPI routes do not.

## Request flow

The intended flow for a database-backed service operation is:

```text
create_app
-> lifespan
-> ApplicationResources
-> request middleware
-> dependency aliases
-> route
-> application handler
-> repository or query adapter
-> response
```

1. Middleware generates a new `X-Request-ID` for every request. It accepts a supplied
   `X-Correlation-ID` only when it matches the bounded safe format; otherwise it generates one.
   Both identifiers enter Logfire baggage and are returned as response headers.
2. Private resolver functions expose settings and lifespan-owned resources through public PEP 695
   dependency aliases. A route that needs PostgreSQL declares `DatabaseSession`, which opens one
   request-owned session and transaction.
3. The route validates its typed API request and converts it into a command or query. It invokes an
   asynchronous application handler rather than placing business orchestration in FastAPI code.
4. The handler coordinates repositories or read-query adapters. Adapters execute SQLAlchemy
   statements through the injected request session and let exceptions propagate to the API
   boundary.
5. An application route converts the result into a typed API response and returns the
   `ApplicationResponse` envelope documented in `docs/api/application-response.md`. FastAPI
   validates and
   serializes the declared response model.

The root and OpenAPI publication endpoints stop at the route: they have no application handler,
repository, query adapter, or database dependency. The OAuth2 token route instead opens a database
transaction, invokes the client-credentials handler, and returns its typed token result inside
`ApplicationResponse` with no-store headers.

When an application workflow makes an outbound call, it depends on a service-owned application
port whose adapter resolves the named lifespan-owned client. Token orchestration remains in that
service, while transport retry is enabled only by
`RequestOptions(retry=PokerLostRetryPolicy())`. A request-owned database transaction must end
before token acquisition, the remote call, or backoff. See
`docs/architecture/inter-service-clients.md` for the complete pattern.

## Safe error path

Registered handlers convert validation, application, HTTP, and SQLAlchemy failures into documented
safe envelopes. They recognize the exact OAuth2 token path only to select its stable
`AUTHSERVICE_*` classification, status, cache headers, and optional Basic challenge; serialization
still uses the central `ApplicationResponse[None]` helper. If another exception escapes, request
middleware records it with the request and correlation identifiers and selects the same
path-specific safe envelope. The response still receives both context headers, while tracebacks
and secrets stay out of the public body. See `docs/api/errors.md` for the exact mappings.

Transaction completion and database error ownership are defined in
`docs/architecture/persistence-and-transactions.md`.
