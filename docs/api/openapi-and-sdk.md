# OpenAPI and SDK

authService publishes FastAPI-generated OpenAPI through `GET /getOpenApi` inside a
`PokerlostResponse`. Built-in `/openapi.json`, `/docs`, and `/redoc` endpoints remain disabled.

The document contains only normal routes, request and response schemas, status responses,
summaries, descriptions, and tags. It has no service-identity extension, Python import metadata,
custom authorization extension, or OAuth2/Basic/API-key security scheme.

Body authentication is represented honestly by request schemas:

- public operations use `PokerlostRequest[Payload]`;
- protected operations use `PokerlostAuthorizedRequest[Payload]` and require
  `authorization.access_token`.

OpenAPI cannot express exact body-token scopes through `securitySchemes`. Exact scopes therefore
remain in the route's `Security(..., scopes=[...])` dependency and the flat SDK method's
`required_scopes`; repository checks compare those sources for implemented protected operations.

The generator validates all source documents together, requires single lowerCamelCase operation
IDs, `POST /<operationId>` for business calls, JSON requests, the canonical response envelope, and
globally unique method/schema names. Generated methods and types are flat. It does not infer scopes
from prose or operation names and does not require service metadata.

`getToken` is generated as `GetToken` and is public at the transport level. Its JSON request owns
client credentials, scopes, and audience. Future-facing SDK stubs do not imply that corresponding
authService endpoints exist.
