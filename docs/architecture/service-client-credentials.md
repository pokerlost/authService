# Planned service-client credentials

This page preserves the intended authService ownership boundary. No operator bootstrap or token-issuing route exists in the current foundation.

## 🧭 Proposed flow

A future operator action would create one service principal, one bound confidential client, exact direct scope and audience grants, and one digest-only credential in one reviewed transaction. `POST /getToken` would accept the canonical `PokerlostRequest` payload with client ID, client secret, exact requested scopes and one service audience; the client secret would never become a bearer header.

The handler would verify active principal/client state and intersect both sets of grants before signing a short-lived service token. An RSA private key would be supplied through an operator-managed secret file, never source, ConfigMap or image. No token should be persisted solely for issuance. Its request/response, replay, revocation and rotation contracts need separate review with the current SDK before implementation.

## 🔒 Boundaries

`accountsService` owns human passwords and account lifecycle; authService owns grants and tokens. Downstream services verify access tokens locally. Network calls must not run inside a local database transaction. Client credentials, token contents, signing material and failure details stay out of logs and documentation examples. Historical Alembic revisions are not evidence that this flow currently runs.

See [SERVICE.md](../../SERVICE.md) for planned ownership and [public surface](../api/public-surface.md) for the two routes that exist now.
