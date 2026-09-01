# authService

`authService` is the PokerLost OAuth2 authorization server. It provides PostgreSQL-backed service
principals and confidential clients, operator bootstrap, and short-lived RS256 access tokens for
the OAuth2 `client_credentials` grant.

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
| `GET` | `/` | `auth.getRoot` | `RootResponse` |
| `GET` | `/openapi.get` | `openapi.get` | `OpenAPIResponse` |
| `POST` | `/oauth.token` | `oauth.token` | `ApplicationResponse[OAuthTokenResponse]` |

The base identifiers shown are the `.env.example` values. Every response uses
`ApplicationResponse`. The OAuth2 token operation retains its form and HTTP Basic request
mechanics, while its access token is returned only as `result.access_token`. See
`docs/api/public-surface.md`.

## Bootstrap a service client

Create the service principal, confidential client, exact grants, and first credential in one local
PostgreSQL transaction:

```bash
authservice bootstrap-service-client \
  --service-slug accountsservice \
  --scope auth.internal.provisionHuman \
  --scope auth.internal.setPrincipalStatus \
  --scope auth.internal.assignRole \
  --scope auth.internal.issueLoginGrant \
  --resource urn:pokerlost:service:authService
```

The command prints the generated client ID and raw client secret only after commit. Store the raw
secret immediately; authService persists only its digest and cannot recover it later.

Service consumers own token acquisition through an application port and a focused adapter that
calls the generated `oauth.token` SDK method. The SDK owns transport and canonical retry only:

```python
from pypokerlost.client.request import RequestOptions
from pypokerlost.client.retry import PokerLostRetryPolicy
```

Retry stays off unless a replay-safe call supplies
`RequestOptions(retry=PokerLostRetryPolicy())`. Token storage and refresh remain consumer-owned;
authService itself creates no outbound client to accountsService or to itself.

The SDK source defines transport, shared authorization contracts, generic request headers, and the
canonical explicit per-call retry policy. A consuming service owns credentials and token
orchestration behind application ports and adapters. The pristine service creates no target
client, credentials, token storage, or retry settings; extension guidance lives in
`docs/architecture/inter-service-clients.md`.

## Development and deployment

Run `make help` for the thin local tool interface. The regular quality entry points are:

```bash
make check
make pre-commit
```

See `docs/development/commands.md` and `docs/development/containers-and-kubernetes.md` for Docker
and Helm workflows.
