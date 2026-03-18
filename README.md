# Sales Analytics Data Platform

[![CI](https://github.com/samuelmaia-analytics/analise-vendas-python/actions/workflows/ci.yml/badge.svg)](https://github.com/samuelmaia-analytics/analise-vendas-python/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Execution](https://img.shields.io/badge/Execution-Batch%20%2B%20App-0f766e)
![Coverage](https://img.shields.io/badge/Coverage-91%25-brightgreen)

Language: [Portuguese (Brazil)](README.pt-BR.md)

This repository is a production-shaped analytics system built around a single sales dataset. It combines a deterministic batch pipeline, a curated analytical layer, a contract-driven data dictionary, and a Streamlit delivery surface that reuses the same domain logic as the pipeline.

The goal is not to simulate a large platform with unnecessary complexity. The goal is to show sound engineering judgment: explicit contracts, reproducible execution, operational traceability, and documentation that matches the code.

## Why this repository exists

This project answers a small but realistic analytics use case:

- transform raw sales events into decision-ready outputs
- validate whether the dataset is reliable enough to consume
- track revenue trend, concentration, and year-over-year movement
- preserve a reproducible execution trail for reprocessing and review

It is intentionally scoped to local file processing, but the engineering patterns are the same ones expected in modern analytics teams: batch orchestration, curated outputs, environment-aware configuration, and delivery discipline.

## What makes it senior

- Single official execution path for the batch workflow
- Clear separation between ingestion, validation, transformation, metrics, reporting, and presentation
- Idempotent outputs with atomic writes
- Run manifests, quality snapshots, KPI snapshots, and failure manifests
- Contract-driven artifact generation and data dictionary generation
- Snapshot history with retention policies by count and age
- Containerized execution and CI validation of the same operational path

## Repository structure

```text
.
|-- .github/
|   |-- ISSUE_TEMPLATE/            # issue intake for bugs and feature requests
|   |-- pull_request_template.md   # PR review contract
|   `-- workflows/                 # CI, release, and delivery automation
|-- app/
|   |-- presentation/              # Streamlit UI helpers, analytics formatting, i18n
|   `-- streamlit_app.py           # dashboard entrypoint
|-- assets/                        # static images used by docs and portfolio material
|-- data/
|   |-- raw/                       # versioned source dataset
|   `-- processed/                 # generated curated artifacts
|-- docs/                          # architecture, data dictionary, and repository standards
|-- legacy/                        # read-only compatibility fallback for old paths
|-- notebooks/                     # isolated exploratory work, kept out of the runtime path
|-- reports/                       # generated executive and analytical extracts
|-- scripts/                       # thin wrappers and repository maintenance utilities
|-- src/sales_analytics/
|   |-- ingestion.py               # source resolution and fingerprinting
|   |-- data_contract.py           # raw/curated schema contracts
|   |-- quality.py                 # quality validation and freshness checks
|   |-- transformations.py         # analytical normalization
|   |-- metrics.py                 # KPI, growth, YoY, Pareto calculations
|   |-- artifacts.py               # curated artifact materialization
|   |-- reporting.py               # report exports
|   |-- batch_pipeline.py          # operational batch orchestration
|   |-- cli.py                     # official CLI
|   |-- config.py                  # runtime and path configuration
|   |-- logging_utils.py           # centralized logging
|   `-- data_dictionary.py         # contract-driven markdown generation
|-- tests/                         # regression, contracts, CLI, app, and pipeline tests
|-- .env.example                   # local runtime configuration template
|-- Dockerfile                     # containerized execution path
|-- Makefile                       # developer shortcuts
|-- Taskfile.yml                   # optional task runner shortcuts
|-- pyproject.toml                 # packaging and tool configuration
|-- README.md
`-- README.pt-BR.md
```

Generated at runtime, not versioned by default:

- `data/state/` for manifests and operational state
- `data/processed/history/` for retained historical curated artifacts
- `reports/history/` for retained historical analytical outputs

## Execution model

The repository exposes two official entrypoints:

- `sales-analytics run-pipeline`
  Runs the batch pipeline, writes curated artifacts, reports, manifests, and optional snapshots.
- `streamlit run app.py`
  Starts the presentation layer for interactive exploration using the same analytical core.

Everything else is secondary. The batch pipeline is the source of truth.

## Data flow

1. Resolve the input dataset from the configured raw path or legacy fallback.
2. Compute a SHA-256 fingerprint for the source file.
3. Validate required columns, invalid dates, invalid values, duplicates, negatives, zeros, and optional freshness thresholds.
4. Normalize the analytical base.
5. Compute KPI, period growth, YoY, and Pareto outputs.
6. Materialize curated outputs:
   - `data/processed/fato_vendas.csv`
   - `data/processed/dim_tempo.csv`
   - `data/processed/dim_produtos.csv`
   - `data/processed/dim_clientes.csv`
7. Publish analytical and operational outputs:
   - `reports/executive_summary.csv`
   - `reports/data_dictionary.md`
   - `reports/cleaned_sales.csv`
   - `reports/periodic_sales.csv`
   - `reports/yoy_sales.csv`
   - `reports/pareto_sales.csv`
8. Persist execution state:
   - `data/state/pipeline_manifest.json`
   - `data/state/quality_report.json`
   - `data/state/kpis.json`
   - `data/state/latest_success.json`
   - `data/state/latest_failure.json`
9. Optionally keep per-run snapshots under:
   - `data/processed/history/<run_id>/`
   - `reports/history/<run_id>/`
   - `data/state/runs/<run_id>/`

## Reliability and operational guarantees

- Idempotent execution: reruns overwrite the deterministic latest targets.
- Atomic persistence: CSV and JSON files are written through temporary files before replacement.
- Reprocessability: the same raw dataset can be rerun with the same logic and produce the same operational path.
- Traceability: every run records a source fingerprint, configuration context, KPI snapshot, and quality snapshot.
- Failure visibility: failed runs produce an explicit failure manifest.
- Historical lineage: optional snapshots preserve point-in-time outputs by `run_id`.
- Snapshot retention: history can be pruned by run count and by age.
- Freshness control: staleness can be evaluated against an environment-defined reference date and threshold.

## Configuration

Runtime behavior is environment-driven. The main variables are:

- `APP_ENV`
- `PIPELINE_NAME`
- `LOG_LEVEL`
- `RAW_DATA_DIR`
- `PROCESSED_DATA_DIR`
- `REPORTS_DIR`
- `PIPELINE_STATE_DIR`
- `ANALYSIS_DATE_COL`
- `ANALYSIS_SALES_COL`
- `ANALYSIS_DIMENSION_COL`
- `ANALYSIS_PERIOD`
- `ENABLE_PIPELINE_SNAPSHOTS`
- `SNAPSHOT_RETENTION_RUNS`
- `SNAPSHOT_RETENTION_DAYS`
- `DATA_FRESHNESS_MAX_AGE_DAYS`
- `DATA_FRESHNESS_REFERENCE_DATE`

Use `.env.example` as the baseline configuration contract.

## Local setup

Install the project and developer dependencies:

```bash
pip install -e ".[dev]"
pre-commit install
```

Create a local `.env` if environment overrides are needed.

## Official commands

Run the full pipeline:

```bash
sales-analytics run-pipeline
```

Export only the executive summary:

```bash
sales-analytics export-summary
```

Generate the contract-driven data dictionary:

```bash
sales-analytics generate-data-dictionary
```

Start the dashboard:

```bash
streamlit run app.py
```

## Quality gates

Run the local engineering gate:

```bash
ruff check .
black --check .
isort . --check-only
mypy src
pytest
```

The same gate is enforced in CI, together with package build validation and container smoke testing.

## Container workflow

Build the image:

```bash
docker build -t sales-analytics-portfolio .
```

Run the batch pipeline in the container:

```bash
docker run --rm -v "$(pwd)/data:/app/data" -v "$(pwd)/reports:/app/reports" sales-analytics-portfolio
```

Smoke test the CLI in the container:

```bash
docker run --rm sales-analytics-portfolio sales-analytics summary
```

Run the dashboard in the container:

```bash
docker run --rm -p 8501:8501 -v "$(pwd)/data:/app/data" -v "$(pwd)/reports:/app/reports" sales-analytics-portfolio streamlit run app.py --server.address 0.0.0.0
```

## Design decisions

- `pandas` remains the execution engine because the dataset and scope do not justify distributed compute.
- Curated outputs follow a lightweight star-schema style because it demonstrates modeling discipline without pretending to be a warehouse platform.
- The Streamlit layer consumes the same analytical logic as the batch pipeline to avoid rule duplication.
- The data dictionary is generated from code-level contracts to reduce documentation drift.
- Legacy paths are kept as read-only fallbacks to preserve compatibility without polluting the main runtime design.

## Trade-offs

- There is no external scheduler or orchestrator.
- There is no object storage or remote state backend.
- Retry logic is intentionally limited because the current system is local-file based.
- Data contracts are strong enough for portfolio-grade discipline, but they are not a full data quality framework.

## Contributing and review expectations

- Contribution workflow: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security reporting: [SECURITY.md](SECURITY.md)
- Architecture notes: [docs/architecture.md](docs/architecture.md)
- Data dictionary: [docs/data_dictionary.md](docs/data_dictionary.md)

## Roadmap

- Add richer freshness assertions and quality thresholds by dataset domain
- Add more explicit semantic-layer style metrics contracts
- Add operational metrics and alert-ready observability hooks
- Add reproducible development environments for faster onboarding
