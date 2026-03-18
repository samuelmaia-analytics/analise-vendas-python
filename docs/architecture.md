# Architecture

## Execution model

The repository now exposes two official execution paths:

- `streamlit run app.py`: presentation-first exploration for recruiters and business users.
- `sales-analytics run-pipeline`: deterministic batch pipeline that reads the raw CSV, validates quality, materializes curated outputs, and writes a run manifest.

The second path is the operational backbone. It makes the project look and behave like a small production analytics service instead of only a notebook/dashboard wrapper.

## Layers

- `src/sales_analytics/`: ingestion, contracts, transformations, metrics, artifact generation, and batch orchestration.
- `app/`: Streamlit presentation layer.
- `scripts/`: thin wrappers around official CLI commands.
- `tests/`: business, contract, and entrypoint regression coverage.

## Data flow

1. Ingestion resolves the source file from configured paths and computes a dataset fingerprint.
2. Quality validation checks required columns, invalid dates, invalid sales values, duplicates, zeros, negatives, and optional freshness thresholds.
3. Transformation normalizes analytical columns and builds a clean sales base.
4. Analytics computes KPI, growth, YoY, and Pareto views.
5. Artifact generation materializes a lightweight star-schema style output:
   - `fato_vendas.csv`
   - `dim_tempo.csv`
   - `dim_produtos.csv`
   - `dim_clientes.csv`
6. Reporting writes `executive_summary.csv`, `data_dictionary.md`, and supporting analytical extracts.
7. State management persists `pipeline_manifest.json`, `quality_report.json`, `kpis.json`, `latest_success.json`, and `latest_failure.json`.
8. When snapshots are enabled, each `run_id` also gets immutable copies under `data/processed/history/`, `reports/history/`, and `data/state/runs/`.
9. Snapshot retention can prune older runs automatically by count and/or age to keep local storage bounded.

## Design decisions

- Raw schema validation is explicit and testable before transformations.
- Writes are atomic to avoid partial files during reprocessing.
- Output paths are deterministic so reruns overwrite the same targets instead of creating drift.
- Run-scoped snapshots provide light historical lineage without requiring an external orchestrator.
- Snapshot retention is configurable so historical lineage does not grow indefinitely.
- Freshness checks are configurable instead of hardcoded, which keeps the sample dataset usable while enabling production-like controls.
- Runtime behavior is configurable through environment variables and `.env`.
- The UI consumes reusable domain logic instead of duplicating transformations.
- Legacy folders remain read-only fallback sources for backward compatibility.
