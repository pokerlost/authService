# authService

`authService` is the Pokerlost token authority. It provides PostgreSQL-backed service principals
and confidential clients, operator bootstrap, and short-lived scope-only RS256 access tokens
through the Pokerlost JSON protocol over HTTPS.

Read the [documentation index](docs/index.md) for the complete guide and `AGENTS.md` for normative engineering rules. Python
3.14 or newer is required.

## 🚀 Install

The mandatory private `pypokerlost` dependency requires GitHub SSH read access:

```bash
cp .env.example .env
ssh-add -l
ssh -T git@github.com
uv lock
uv sync --locked
```

Replace local placeholders in `.env`, provide an RSA private key at the configured
`AUTHSERVICE_JWT__PRIVATE_KEY_PATH`, and never store secrets or private keys in the repository.

## Run

```bash
make run
```

## HTTP surface

| method | path | operation_id | response |
| --- | --- | --- | --- |
| `GET` | `/` | `getRoot` | `PokerlostResponse[None]` |
| `GET` | `/getOpenApi` | `getOpenApi` | OpenAPI 3.1 document |
| `POST` | `/getToken` | `getToken` | `PokerlostResponse[PokerlostToken]` |

The infrastructure endpoints and `getToken` have no access-token scope requirement. `getToken`
receives client credentials, exact scopes, and an exact target service name only in
`PokerlostRequest.payload`; these operation credentials are not an access-token header.

## Bootstrap a service client

Create one service principal, confidential client, exact grants, and first credential in a local
PostgreSQL transaction:

```bash
authservice bootstrap-service-client \
  --service-slug accountsservice \
  --scope auth.internal.provisionHuman \
  --scope auth.internal.setPrincipalStatus \
  --scope auth.internal.replacePrincipalScopes \
  --scope auth.internal.issueLoginGrant \
  --audience authService
```

The command prints the generated client ID and raw secret only after commit. Store that secret
immediately; authService persists only its digest. authService creates no outbound client to
itself or accountsService. See `docs/api/public-surface.md` and
`docs/architecture/service-client-credentials.md`.

## Development and deployment

Run `make help` for the local tool interface. Regular quality entry points are:

```bash
make check
make pre-commit
```

Production access requires HTTPS/TLS. The generated Helm ClusterIP is an internal target and must
remain behind trusted TLS termination.
