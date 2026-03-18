# Sales Analytics Pipeline

[![CI](https://github.com/samuelmaia-analytics/analise-vendas-python/actions/workflows/ci.yml/badge.svg)](https://github.com/samuelmaia-analytics/analise-vendas-python/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Batch](https://img.shields.io/badge/Mode-Batch%20%2B%20App-0f766e)
![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen)

Language: [Portuguese (Brazil)](README.pt-BR.md)

This repository is a small but production-shaped analytics system. It ingests a raw sales CSV, enforces basic data quality gates, materializes curated outputs, publishes an executive summary, and exposes the same analytical core to a Streamlit app.

## Business value

The pipeline answers the questions that matter in a sales review cycle:

- how much revenue was generated and how concentrated it is
- whether growth is improving or decelerating over time
- which periods are strongest and weakest
- whether the dataset is reliable enough to support decisions

The repository is intentionally scoped to a single dataset, but the engineering patterns target real portfolio signal: reproducibility, traceability, separation of concerns, and testability.

## Architecture

```text
.
|-- .github/workflows/          # CI pipelines
|-- app/                        # Streamlit presentation layer
|   |-- presentation/           # UI components, i18n, data adapters
|   `-- streamlit_app.py        # dashboard entrypoint
|-- assets/                     # static images for docs and portfolio material
|-- data/
|   |-- raw/                    # versioned input dataset
|   `-- processed/              # generated curated outputs
|-- docs/                       # architecture and engineering notes
|-- legacy/                     # backward-compatible source/output fallback
|-- notebooks/                  # exploratory analysis kept isolated
|-- reports/                    # generated executive and analytical extracts
|-- scripts/                    # repository maintenance scripts
|-- src/sales_analytics/
|   |-- cli.py                  # official command-line entrypoint
|   |-- ingestion.py            # source resolution and dataset fingerprinting
|   |-- data_contract.py        # schema expectations for raw and curated data
|   |-- quality.py              # data quality gates
|   |-- transformations.py      # analytical normalization
|   |-- metrics.py              # KPI, growth, YoY, Pareto logic
|   |-- artifacts.py            # curated artifact materialization
|   |-- batch_pipeline.py       # batch orchestration and run manifest
|   |-- reporting.py            # executive output publishing
|   |-- config.py               # environment-aware runtime and paths
|   |-- logging_utils.py        # centralized logging
|   `-- settings.py             # Streamlit runtime limits
|-- tests/                      # regression, contract, CLI, and app tests
|-- .env.example                # local runtime configuration template
|-- app.py                      # root entrypoint for Streamlit
|-- pyproject.toml              # packaging and tool configuration
`-- README.md
```

Generated at runtime, not versioned by default:

- `data/state/` for manifests and execution state
- files inside `data/processed/` and `reports/` are overwritten by pipeline runs

## Data flow

1. Resolve the input dataset from `data/raw` or the legacy fallback path.
2. Compute a SHA-256 fingerprint for the source file.
3. Validate schema and quality constraints before analysis.
4. Normalize the analytical base.
5. Compute KPI, period growth, YoY, and Pareto views.
6. Materialize curated outputs:
   - `data/processed/fato_vendas.csv`
   - `data/processed/dim_tempo.csv`
   - `data/processed/dim_produtos.csv`
   - `data/processed/dim_clientes.csv`
7. Persist operational metadata:
   - `reports/executive_summary.csv`
   - `reports/cleaned_sales.csv`
   - `reports/periodic_sales.csv`
   - `reports/yoy_sales.csv`
   - `reports/pareto_sales.csv`
   - `data/state/pipeline_manifest.json`
   - `data/state/quality_report.json`
   - `data/state/kpis.json`
   - `data/state/latest_success.json`
   - `data/state/latest_failure.json` when a run fails
8. Optionally snapshot each execution under:
   - `data/processed/history/<run_id>/`
   - `reports/history/<run_id>/`
   - `data/state/runs/<run_id>/`
9. Generate a contract-driven dictionary:
   - `reports/data_dictionary.md`

## Reliability choices

- Idempotent writes: rerunning the batch pipeline rewrites deterministic targets instead of creating duplicate versions.
- Atomic persistence: CSV and JSON outputs are written through temporary files and replaced only after success.
- Reprocessability: the pipeline can be rerun from the same raw input with consistent artifact paths.
- Traceability: each run records dataset fingerprint, runtime parameters, KPI snapshot, and quality summary.
- Historical auditability: optional per-run snapshots preserve exactly what each execution produced.
- Snapshot retention: historical runs can be pruned automatically with an environment-defined retention window.
- Time-based retention: old snapshots can also be pruned by age, not only by run count.
- Freshness checks: the pipeline can flag stale data against an environment-defined reference date and age threshold.
- Backward compatibility: legacy input folders remain read-only fallbacks.

## Stack

- Python
- Pandas
- Streamlit
- Plotly
- Pytest
- Ruff
- Black
- isort
- Mypy
- pre-commit
- GitHub Actions

## Running locally

Install dependencies:

```bash
pip install -e ".[dev]"
```

Create a local environment file if needed by copying `.env.example` to `.env`.

```bash
# example
# copy .env.example to .env
```

Run the full batch pipeline:

```bash
sales-analytics run-pipeline
```

Generate only the executive summary:

```bash
sales-analytics export-summary
```

Generate the contract-driven data dictionary:

```bash
sales-analytics generate-data-dictionary
```

Open the Streamlit application:

```bash
streamlit run app.py
```

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

See `.env.example` for defaults.

## Quality controls

Run the local quality suite:

```bash
ruff check .
black --check .
isort . --check-only
mypy src
pytest
```

`pre-commit` mirrors the same core checks for local guardrails, and GitHub Actions validates lint, typing, tests, and package build.

## Technical decisions

- Pandas was kept as the main engine because the dataset volume and portfolio scope do not justify Spark or distributed infrastructure.
- The star-schema output is intentionally lightweight: enough to show modeling discipline without pretending to be a warehouse platform.
- The repository keeps both batch and app entrypoints because that reflects a common analytics product pattern: one trusted data backbone, multiple consumers.
- The data dictionary is generated from code-level contracts so documentation and implementation drift less over time.

## Trade-offs

- There is no external orchestrator, scheduler, or object storage integration. That would be disproportionate for this scope.
- Retries are not implemented against remote systems because the pipeline currently reads local files only.
- Data contracts are schema-level and sanity-level, not a full Great Expectations style framework.

## Container

Build the image:

```bash
docker build -t sales-analytics-portfolio .
```

Run the batch pipeline in a container:

```bash
docker run --rm -v "$(pwd)/data:/app/data" -v "$(pwd)/reports:/app/reports" sales-analytics-portfolio
```

Smoke test the CLI in the container:

```bash
docker run --rm sales-analytics-portfolio sales-analytics summary
```

Run the dashboard in a container:

```bash
docker run --rm -p 8501:8501 -v "$(pwd)/data:/app/data" -v "$(pwd)/reports:/app/reports" sales-analytics-portfolio streamlit run app.py --server.address 0.0.0.0
```

## Roadmap

- Add partitioned outputs and historical snapshots for multi-run comparisons.
- Introduce data freshness assertions and source-level SLAs.
- Publish containerized execution and reproducible dev environments.
- Add warehouse/dbt-style models for downstream semantic consumption.
