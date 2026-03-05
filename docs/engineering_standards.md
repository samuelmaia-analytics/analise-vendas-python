# Engineering Standards

## Objective

Maintain a production-grade analytics repository with clear boundaries between UI, business logic, data contracts, and tests.

## Conventions

- `app/`: presentation layer only (Streamlit views and interactions)
- `src/`: reusable logic (contracts, metrics, transformations, artifacts)
- `tests/`: test suite aligned with `src/` responsibilities
- `data/raw`: immutable source datasets
- `data/processed`: generated artifacts (versionable when relevant)
- `reports/`: stakeholder-facing documents

## Definition of Done

A change is considered complete only when:

1. `ruff check .` passes
2. `mypy src` passes
3. `pytest` passes with minimum 80% coverage on `src`
4. `pre-commit run --all-files` passes
5. README docs are updated when behavior or structure changes

## Backward Compatibility

Legacy folders are isolated under `legacy/` (`legacy/dados/`, `legacy/dados_processados/`) and kept only for compatibility; all new development must target `data/raw` and `data/processed`.
