# API overview

This page introduces the HTTP API foundation generated for `authService` and points to the
canonical contract pages for authoring service operations.

## Transport and operations

FastAPI owns HTTP routing, request validation, response serialization, and OpenAPI generation.
Business service methods use exact two-segment lowerCamelCase operation IDs and matching paths;
their naming and body rules are defined in `docs/api/operation-contract.md`.

An operation accepts one named, typed JSON request body when it needs input. A parameterless operation
omits the body. Transport details do not become application or domain values: a route translates a
validated request into application input and translates the application result into a public
response model.

## Responses and errors

PokerLost application operations return the four-field `ApplicationResponse` envelope documented
in `docs/api/application-response.md`. The envelope distinguishes success from failure while
keeping the successful result strongly typed. Central exception handlers convert the supported
failure categories into safe public responses described in `docs/api/errors.md`.

`POST /oauth.token` is a narrow request-shape exception: it accepts a form and HTTP Basic client
authentication instead of an application JSON request. Its success and handled failures still use
`ApplicationResponse`, and validation never exposes FastAPI's `detail` shape. Token responses also
carry the required no-store headers.

## OpenAPI and generated clients

The service disables FastAPI's built-in schema and documentation URLs. It publishes the generated
OpenAPI 3.1 document inside `ApplicationResponse` through the configured publication operation.
The document is the
input to the authoritative `pypokerlost` method generator; PokerLost inter-service calls use the
generated methods and SDK client rather than a service-owned HTTP transport. See
`docs/api/openapi-and-sdk.md` for the publication and client boundary.

The current endpoint inventory is maintained in `docs/api/public-surface.md`.
