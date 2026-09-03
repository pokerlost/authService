# API overview

authService uses FastAPI with the Pokerlost JSON protocol over HTTPS.

Every business operation is `POST /<operationId>` with one lowerCamelCase verb name. Every input
uses the pure JSON `PokerlostRequest`; a protected operation additionally receives a bearer access
token in the standard `Authorization` header. Every business result uses `PokerlostResponse`.

`GET /` and `GET /getOpenApi` are public bodyless infrastructure endpoints. The only implemented
business operation is public `POST /getToken`; it receives service client credentials, exact
scopes, and audience only inside `PokerlostRequest.payload`. authService currently has no
protected route, concrete token verifier, or outbound service client. `GET /getOpenApi` returns the
raw generated OpenAPI document.

Read `docs/api/operation-contract.md` for operation rules,
`docs/api/pokerlost-response.md` for the response invariant,
`docs/api/header-authorization.md` for exact scopes and local verification, and
`docs/api/openapi-and-sdk.md` for publication/generation.
