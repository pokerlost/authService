# Python style

This page summarizes the executable Python quality contract for the generated service.

## Executable source of truth

The project requires Python 3.14 or newer. `pyproject.toml` is authoritative
for the Python requirement, Ruff target, 88-character line length, lint selection, strict mypy
configuration, source roots, and declared development dependencies. `uv.lock` records their
resolved versions.

Ruff owns formatting and linting. Mypy runs in strict mode with Python 3.14 semantics. Pre-commit
invokes those tools through `uv run --locked`, so hook versions come from the project lock instead
of an independent hook environment. Use the commands documented in
`docs/development/commands.md`.

Do not add broad `# noqa` or `# type: ignore` suppressions. A narrow suppression requires a specific, reviewable reason and must not hide an avoidable typing or lint defect.

## Language and dependency conventions

- Use modern Python 3.14 syntax.
- Expose FastAPI dependencies through PEP 695 type aliases backed by private resolver functions.
- Keep public request, response, application, domain, and persistence models in their established layers.
- Preserve explicit imports and focused package facades.
- Keep async boundaries explicit and avoid blocking work in request paths.
- Never log or embed credentials, tokens, private keys, or database URLs.

## Artifact names

Project-owned modules, functions, methods, variables, and fields use `snake_case`; classes use
`CapWords`, and constants use `UPPER_SNAKE_CASE`. External operation IDs, scope strings, HTTP
fields, repository names, and framework hooks keep their published spelling.

The generated `AGENTS.md` owns project-specific naming exceptions, layer rules,
operation-package naming, and public API conventions. Keep this page as a tooling summary rather
than a duplicate rulebook.
