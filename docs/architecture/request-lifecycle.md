# Request lifecycle

This page traces composition, server-owned request context, authorization, application execution,
and response handling.

## Composition

`create_app()` resolves settings, configures observability, constructs FastAPI, and registers
request middleware, exception handlers, flat routers, and instrumentation. Lifespan creates the
database engine/session factory and one process-owned RS256 signer, then stores them with the
optional `PokerlostTokenVerifier` in `ApplicationResources`.

authService currently supplies no verifier because it has no protected route. A real local
verifier is passed only when an implemented route requires protection; missing protected
composition fails closed.

## Inbound flow

```text
FastAPI
→ server-generated request ID
→ dependencies
→ flat route
→ application handler
→ persistence adapter
→ plain success mapping
→ FastAPI response_model
→ PokerlostResponse JSON
```

The request ID is generated server-side and exists only in request state and telemetry. No caller
correlation value is accepted or returned as a transport contract.

Every route receives `PokerlostRequest[Payload]`. A protected route also declares exact scopes
through `Security`. The dependency parses one bearer header, invokes the local verifier for the
exact service-name audience, and checks every scope before the route executes.

Pydantic request models parse and validate wire values before routes translate payloads into
application commands or queries. Routes translate application results into plain mappings;
FastAPI validates and serializes them through the declared `response_model`. Central handlers
normalize validation, application, database, authentication, authorization, and unexpected
failures without exposing submitted input.

`POST /getToken` opens a request-owned database transaction, invokes the client-credentials
handler, and returns plain token data for response-model serialization. Root and OpenAPI routes
open no database transaction.

## Transactions and outbound calls

A route that declares `DatabaseSession` owns one async transaction. It must end before token
acquisition, outbound SDK calls, retry sleep, or subsequent attempts. Outbound clients use retry
then authentication middleware as documented in `docs/architecture/inter-service-clients.md`.

The root and OpenAPI routes stop at the route layer and open no database transaction.
