# Header authorization

Protected future Pokerlost operations accept exactly one access token through `Authorization: Bearer <token>`. The present service has no protected business route and no configured verifier. Missing verifier configuration fails closed when a future protected route is added.

`src/authservice/authorization.py` owns the standard FastAPI OAuth2 declaration, exact audience/scope verification boundary, and canonical auth errors. `src/authservice/scopes.py` owns the service's sole exact dotted-scope catalog and OpenAPI descriptions; it is empty today. The public root, actual `/getOpenApi`, and health probes are infrastructure exceptions. Tokens, cookies, and request bodies are never logged as an authorization workaround.

The SDK's public scope catalog and HTTP transport remain independent. Adding a server operation requires a real route, exact scopes, a local verifier implementation, and an OpenAPI/SDK compatibility review; no allow-all verifier or invented operation exists in this foundation.
