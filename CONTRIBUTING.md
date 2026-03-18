# Contributing

This repository is maintained as a production-shaped data engineering portfolio project. Contributions are expected to preserve that bar: clear contracts, deterministic behavior, and documentation that matches the runtime.

## What good contributions look like

- small, reviewable changes
- explicit technical rationale
- tests for behavioral changes
- updated documentation when structure, runtime, or contracts change
- no duplication of business logic outside the official pipeline or shared domain layer

## Repository boundaries

Use these boundaries when contributing:

- `src/sales_analytics/`
  Source of truth for ingestion, validation, transformations, metrics, reporting, configuration, and pipeline orchestration.
- `app/`
  Presentation layer only. UI code should consume reusable domain logic instead of reimplementing transformations.
- `scripts/`
  Thin wrappers or maintenance utilities only. Do not add parallel business logic here.
- `tests/`
  Regression, contract, integration, and entrypoint coverage.
- `docs/`
  Technical documentation that must remain aligned with the runtime behavior.

## Local setup

```bash
pip install -e ".[dev]"
pre-commit install
```

If environment overrides are needed, copy `.env.example` to `.env` and adjust only the variables required for your local run.

## Development workflow

1. Create a branch from `main`.
2. Understand the current architecture before editing.
3. Prefer modifying the official pipeline and shared domain modules over adding new side paths.
4. Keep changes narrow and explain trade-offs in the PR.
5. Run the required quality gates before opening a pull request.

## Mandatory quality gates

```bash
ruff check .
black --check .
isort . --check-only
mypy src
pytest
```

Recommended additional checks when touching operational paths:

```bash
sales-analytics run-pipeline
sales-analytics generate-data-dictionary
docker build -t sales-analytics-portfolio .
docker run --rm sales-analytics-portfolio sales-analytics summary
```

## Contribution rules

- Do not introduce sensitive data, secrets, or personal tokens.
- Do not add fake enterprise complexity that the project does not justify.
- Do not preserve duplicated legacy logic if it conflicts with the official execution path.
- Do not update documentation aspirationally. Keep it aligned with the repository as it exists.
- When changing schemas, outputs, runtime configuration, or CLI behavior:
  - update tests
  - update relevant docs
  - update the data dictionary generator if needed

## Pull request review standard

Every PR should make it easy to answer:

- what changed
- why the change was necessary
- how the change was validated
- what contracts or operational paths were affected

## Pull request checklist

- [ ] Change is scoped and reviewable
- [ ] Tests were added or updated when behavior changed
- [ ] Docs were updated when runtime behavior, structure, or contracts changed
- [ ] No duplicate business logic was introduced
- [ ] Quality gates passed locally
- [ ] No secrets or unsafe defaults were introduced

## When to open an issue first

Open an issue before implementation when the change:

- alters the official pipeline contract
- changes runtime defaults
- introduces a new operational dependency
- affects artifact naming or report structure
- changes the repository’s public positioning for portfolio/recruiter audiences
