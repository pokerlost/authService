.DEFAULT_GOAL := help

UV ?= uv
HTTP_HOST ?= 127.0.0.1
HTTP_PORT ?= 8000
HELM_CHART := deploy/helm/authservice

.PHONY: help install lock lock-check run serve format format-check lint typecheck compile docs-check pre-commit check check-full db-upgrade db-downgrade db-revision docker-build helm-lint helm-template

help:
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies from uv.lock
	$(UV) sync --locked

lock: ## Resolve dependencies and write uv.lock
	$(UV) lock

lock-check: ## Verify that uv.lock matches pyproject.toml
	$(UV) lock --check

run: ## Run local development server; DATABASE_URL must be supplied
	$(UV) run --locked uvicorn authService.app:createApp --factory --reload --host "$(HTTP_HOST)" --port "$(HTTP_PORT)"

serve: ## Run production server without reload
	$(UV) run --locked uvicorn authService.app:createApp --factory --host "$(HTTP_HOST)" --port "$(HTTP_PORT)"

format: ## Apply Ruff lint fixes and formatting
	$(UV) run --locked ruff check --fix .
	$(UV) run --locked ruff format .

format-check: ## Check Ruff formatting without changing files
	$(UV) run --locked ruff format --check .

lint: ## Run Ruff lint without changing files
	$(UV) run --locked ruff check .

typecheck: ## Run strict mypy
	$(UV) run --locked mypy

compile: ## Compile the installed package, migrations, and existing documentation tool
	$(UV) run --locked python -m compileall -q src/authService migrations/env.py scripts

docs-check: ## Validate the existing documentation contract
	$(UV) run --locked python scripts/check_documentation.py

pre-commit: ## Run existing pre-commit hooks against all files
	$(UV) run --locked pre-commit run --all-files --show-diff-on-failure

check: lock-check format-check lint typecheck compile docs-check ## Run regular non-test checks

check-full: check pre-commit ## Run regular checks and existing pre-commit hooks

db-upgrade: ## Apply reviewed revisions to the configured database
	$(UV) run --locked alembic upgrade head

db-downgrade: ## Downgrade one reviewed revision on a disposable database
	$(UV) run --locked alembic downgrade -1

db-revision: ## Create an empty revision for a separately reviewed schema change
	@test -n "$(message)" || (echo "message is required" >&2; exit 2)
	$(UV) run --locked alembic revision -m "$(message)"

docker-build: ## Build local image with private SDK Git access
	docker build --ssh default --secret id=github_known_hosts,src="$$HOME/.ssh/known_hosts" -t pokerlost-authservice:local .

helm-lint: ## Lint the retained Helm chart
	helm lint "$(HELM_CHART)"

helm-template: ## Render the retained Helm chart locally
	helm template authservice "$(HELM_CHART)"
