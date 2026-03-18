# Documentation Index

This folder contains the technical reference layer for the repository. The main README explains positioning and usage; the files below explain how the system is structured and operated.

## Core references

- Engineering standards: [engineering_standards.md](engineering_standards.md)
- Architecture: [architecture.md](architecture.md)
- Data dictionary: [data_dictionary.md](data_dictionary.md)
- Repository print view: [print_view.md](print_view.md)

## Repository-facing references

- Main README: [../README.md](../README.md)
- Portuguese README: [../README.pt-BR.md](../README.pt-BR.md)
- Contribution guide: [../CONTRIBUTING.md](../CONTRIBUTING.md)
- Security policy: [../SECURITY.md](../SECURITY.md)
- Changelog: [../CHANGELOG.md](../CHANGELOG.md)

## Operational entrypoints

- Official batch pipeline: `sales-analytics run-pipeline`
- Contract-driven data dictionary: `sales-analytics generate-data-dictionary`
- Streamlit app: `streamlit run app.py`
- Container CLI smoke test: `docker run --rm sales-analytics-portfolio sales-analytics summary`

## Documentation rules

- Documentation must describe the repository as it exists now, not as an aspirational future state.
- When runtime behavior, CLI surface, artifact contracts, or repository structure changes, update the relevant docs in the same change set.
- Prefer contract-driven or generated documentation where possible to reduce drift.
