# Installation

This page prepares a local checkout of `authService` with its locked Python 3.14 environment.

## Prerequisites

Install Python 3.14 or newer, `uv`, and Git. An isolated PostgreSQL instance is needed to
verify readiness or run migrations. The application does not start one.

The project installs `pypokerlost` from a pinned private GitHub SSH source. Confirm that an authorized key is available through the SSH agent and that GitHub recognizes it:

```bash
ssh-add -l
```

Never copy a private key into the repository or place one in a settings file.

## Configure and install

Run the setup from the repository root:

```bash
uv sync --locked
```

Supply `DATABASE_URL` through a private process environment when running the service.
The application does not load `.env` automatically. `uv.lock` is committed; run `uv lock`
only when deliberately changing dependencies.

See `docs/getting-started/configuration.md` for the environment variable contract and
`docs/development/commands.md` for the Makefile wrappers.
