# authService

`authService` is the Pokerlost token authority. It provides PostgreSQL-backed service principals
and confidential clients, operator bootstrap, and short-lived RS256 access tokens through the
private body-only Pokerlost JSON protocol over HTTPS.

Read `docs/index.md` for the complete guide and `AGENTS.md` for normative engineering rules.
Python 3.14 or newer is required.

## Install

The mandatory private `pypokerlost` dependency requires GitHub SSH read access. Create local
configuration, verify the SSH identity, and install the locked environment:

```bash
cp .env.example .env
ssh-add -l
ssh -T git@github.com
uv lock
uv sync --locked
```

Replace the local placeholders in `.env`, provide an RSA private key at the configured
`AUTHSERVICE_JWT__PRIVATE_KEY_PATH`, and keep secrets and private keys outside the repository.
See `docs/getting-started/installation.md` and `docs/getting-started/configuration.md` for details.

## Run

```bash
make run
```

## HTTP surface

| method | path | operation_id | response_model |
| --- | --- | --- | --- |
| `GET` | `/` | `getRoot` | `PokerlostResponse[None]` |
| `GET` | `/getOpenApi` | `getOpenApi` | `PokerlostResponse[dict[str, JSONValue]]` |
| `POST` | `/getToken` | `getToken` | `PokerlostResponse[PokerlostToken]` |

The base identifiers shown are the `.env.example` values. `getToken` receives client credentials,
exact scopes, and the logical target audience only in `PokerlostRequest.payload`. It does not
accept authentication headers, cookies, query parameters, or form data. See
`docs/api/public-surface.md`.

## Bootstrap a service client

Create the service principal, confidential client, exact grants, and first credential in one local
PostgreSQL transaction:

```bash
authservice bootstrap-service-client \
  --service-slug accountsservice \
  --scope auth.internal.provisionHuman \
  --scope auth.internal.setPrincipalStatus \
  --scope auth.internal.assignPrincipalRole \
  --scope auth.internal.issueLoginGrant \
  --resource urn:pokerlost:service:authService
```

The command prints the generated client ID and raw client secret only after commit. Store the raw
secret immediately; authService persists only its digest and cannot recover it later.

Service consumers use the generated `GetToken` method through
`PokerlostAuthorizationMiddleware`. The SDK owns body authorization and canonical retry:

```python
from pypokerlost.client import PokerlostRequestOptions
from pypokerlost.middleware import PokerlostAuthorizationMiddleware, PokerlostRetryPolicy
```

Retry stays off unless a replay-safe call supplies
`PokerlostRequestOptions(retry_policy=PokerlostRetryPolicy())`. authService itself creates no
outbound client to accountsService or to itself.

The SDK source defines transport, the two JSON request envelopes, shared authorization values,
middleware, and the canonical explicit per-call retry policy. Authentication material and
`retry_after` never use HTTP headers. The pristine service creates no target client, credentials,
token storage, or retry settings; extension guidance lives in
`docs/architecture/inter-service-clients.md`.

## Development and deployment

Run `make help` for the thin local tool interface. The regular quality entry points are:

```bash
make check
make pre-commit
```

See `docs/development/commands.md` and `docs/development/containers-and-kubernetes.md` for Docker
and Helm workflows.
