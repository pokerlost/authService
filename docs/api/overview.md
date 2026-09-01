# API overview

This page introduces the HTTP API foundation generated for `authService` and points to the
canonical contract pages for authoring service operations.

## Transport and operations

FastAPI owns HTTP routing, request validation, response serialization, and OpenAPI generation.
Business service methods use single lowerCamelCase operation IDs and matching paths;
their naming and body rules are defined in `docs/api/operation-contract.md`.

An operation accepts one typed JSON request envelope when it needs input. Public operations use
`PokerlostRequest`; protected operations use `PokerlostAuthorizedRequest`. A parameterless
infrastructure operation omits the body.

## Responses and errors

Pokerlost application operations return the five-field `PokerlostResponse` envelope documented
in `docs/api/application-response.md`. The envelope distinguishes success from failure while
keeping the successful result strongly typed. Central exception handlers convert the supported
failure categories into safe public responses described in `docs/api/errors.md`.

`POST /getToken` accepts service client credentials, exact scopes, and audience only inside the
JSON payload. Validation never exposes FastAPI's `detail` shape or submitted secret values.

## OpenAPI and generated clients

The service disables FastAPI's built-in schema and documentation URLs. It publishes the generated
OpenAPI 3.1 document inside `PokerlostResponse` through the configured publication operation.
The document is the
input to the authoritative `pypokerlost` method generator; PokerLost inter-service calls use the
generated methods and SDK client rather than a service-owned HTTP transport. See
`docs/api/openapi-and-sdk.md` for the publication and client boundary.

The current endpoint inventory is maintained in `docs/api/public-surface.md`.
