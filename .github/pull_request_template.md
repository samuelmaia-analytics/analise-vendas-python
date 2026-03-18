## Summary

Describe the change in one short paragraph. Focus on the technical problem and why this change was necessary.

## Scope

- [ ] Pipeline/runtime
- [ ] Data contracts / schema
- [ ] Reporting / artifacts
- [ ] Streamlit presentation
- [ ] Tooling / CI / docs

## Technical context

What was wrong or missing before this change?

## What changed

- 

## Validation

- [ ] `ruff check .`
- [ ] `black --check .`
- [ ] `isort . --check-only`
- [ ] `mypy src`
- [ ] `pytest`

Additional validation performed:

- [ ] `sales-analytics run-pipeline`
- [ ] `sales-analytics generate-data-dictionary`
- [ ] `docker build -t sales-analytics-portfolio .`
- [ ] `docker run --rm sales-analytics-portfolio sales-analytics summary`

## Risk assessment

- Operational risk:
- Contract/schema risk:
- Backward-compatibility impact:

## Reviewer checklist

- [ ] Change follows the repository architecture
- [ ] No parallel business logic path was introduced
- [ ] Tests are sufficient for the change
- [ ] Docs match the implemented behavior
- [ ] No secrets or unsafe defaults were introduced
