# Contributing Guide

## Scope

This repository follows an analytics-engineering standard with clear boundaries:
- `app/` for UI
- `src/` for business/data logic
- `tests/` for automated tests

## Local Setup

```bash
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

## Development Workflow

1. Create a branch from `main`.
2. Implement changes in small, reviewable commits.
3. Keep docs updated when behavior or structure changes.
4. Run quality gates before opening PR.

## Quality Gates (Required)

```bash
ruff check .
pytest -q
pre-commit run --all-files
```

## Pull Request Checklist

- [ ] Code follows project structure conventions
- [ ] Tests added/updated for behavior changes
- [ ] README/docs updated when needed
- [ ] CI is green
