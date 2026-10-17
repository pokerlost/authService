# Request lifecycle

This page traces composition, server-owned request context, authorization, application execution,
and response handling.

## Composition

`create_app()` receives or validates settings and constructs FastAPI without opening network
connections. Lifespan creates and closes the per-worker database engine and session factory.
The optional `PokerlostTokenVerifier` is supplied only for an implemented protected route.

The pristine service supplies no verifier. A concrete service passes a real local verifier only
when it implements a protected route. Missing protected composition fails closed.

## Inbound flow

```text
FastAPI
→ validated request ID
→ dependencies
→ flat route
→ application handler
→ persistence adapter
→ plain success mapping
→ FastAPI response_model
```

The bounded request ID is generated when absent and returned in the response header. Invalid
caller values are replaced. Bodies, tokens and DSNs are never logged.

Every business route receives the pure JSON `PokerlostRequest[Payload]`. A protected route also
declares a non-empty exact scope set through `Security`. The standard OAuth2 dependency parses the
bearer header, invokes the local verifier for the exact service audience, and checks every scope
before the route executes.

Future routes must translate validated payloads into actual application scenarios and return
SDK-compatible responses. Current routes are infrastructure only. Central handlers normalize
validation, database, authorization and unexpected failures without exposing submitted input.

An expired token is rejected before entering the endpoint handler or beginning business effects.
That ordering is the safety invariant for the SDK's one permitted reactive refresh and replay.

## Transactions and outbound calls

A route that declares `DatabaseSession` uses a function-scoped dependency that commits on success
and rolls back on failure before response send. It must end before token
acquisition, outbound SDK calls, retry sleep, or subsequent attempts. Outbound clients use retry
then authorization middleware as documented in `docs/architecture/inter-service-clients.md`.

The root, OpenAPI and liveness routes open no request database transaction.
