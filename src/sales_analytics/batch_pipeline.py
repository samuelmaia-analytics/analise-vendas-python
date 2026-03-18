from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
from typing import Mapping

import pandas as pd

from .artifacts import generate_processed_artifacts
from .config import get_project_paths, get_runtime_config
from .data_dictionary import export_data_dictionary
from .exceptions import SalesAnalyticsError
from .ingestion import load_sales_dataset
from .io_utils import atomic_write_csv, atomic_write_json
from .logging_utils import get_logger
from .pipeline import run_sales_analysis
from .reporting import export_executive_summary

LOGGER = get_logger(__name__)


@dataclass(frozen=True)
class BatchPipelineResult:
    run_id: str
    manifest_path: Path
    quality_report_path: Path
    kpis_path: Path
    output_files: tuple[Path, ...]


def _write_failure_state(
    *,
    state_dir: Path,
    runtime_pipeline_name: str,
    environment: str,
    source_path: Path | None,
    error: Exception,
) -> Path:
    failure_payload = {
        "status": "failed",
        "pipeline_name": runtime_pipeline_name,
        "environment": environment,
        "source_path": str(source_path) if source_path is not None else None,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "failed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    failure_path = atomic_write_json(failure_payload, state_dir / "pipeline_failure.json")
    atomic_write_json(failure_payload, state_dir / "latest_failure.json")
    return failure_path


def _snapshot_run_outputs(
    *,
    run_id: str,
    output_dir: Path,
    reports_dir: Path,
    state_dir: Path,
    cleaned_data: pd.DataFrame,
    periodic_sales: pd.DataFrame,
    yoy_sales: pd.DataFrame,
    pareto_sales: pd.DataFrame,
    quality_payload: Mapping[str, object],
    kpis_payload: Mapping[str, object],
    manifest_payload: Mapping[str, object],
    artifact_files: list[Path],
) -> dict[str, list[str] | str]:
    processed_snapshot_dir = output_dir / "history" / run_id
    reports_snapshot_dir = reports_dir / "history" / run_id
    state_snapshot_dir = state_dir / "runs" / run_id

    snapshot_artifacts: list[str] = []
    for artifact_file in artifact_files:
        snapshot_target = processed_snapshot_dir / artifact_file.name
        snapshot_target.parent.mkdir(parents=True, exist_ok=True)
        snapshot_target.write_bytes(artifact_file.read_bytes())
        snapshot_artifacts.append(str(snapshot_target))

    snapshot_reports = [
        str(atomic_write_csv(cleaned_data, reports_snapshot_dir / "cleaned_sales.csv")),
        str(atomic_write_csv(periodic_sales, reports_snapshot_dir / "periodic_sales.csv")),
        str(atomic_write_csv(yoy_sales, reports_snapshot_dir / "yoy_sales.csv")),
        str(atomic_write_csv(pareto_sales, reports_snapshot_dir / "pareto_sales.csv")),
    ]
    snapshot_state = {
        "manifest": str(atomic_write_json(dict(manifest_payload), state_snapshot_dir / "pipeline_manifest.json")),
        "quality": str(atomic_write_json(dict(quality_payload), state_snapshot_dir / "quality_report.json")),
        "kpis": str(atomic_write_json(dict(kpis_payload), state_snapshot_dir / "kpis.json")),
    }
    return {
        "processed_dir": str(processed_snapshot_dir),
        "reports_dir": str(reports_snapshot_dir),
        "state_dir": str(state_snapshot_dir),
        "artifacts": snapshot_artifacts,
        "reports": snapshot_reports,
        "state_files": list(snapshot_state.values()),
    }


def _apply_snapshot_retention(
    *,
    output_dir: Path,
    reports_dir: Path,
    state_dir: Path,
    keep_runs: int | None,
    max_age_days: int | None,
) -> None:
    state_history_dir = state_dir / "runs"
    if not state_history_dir.exists():
        return

    run_directories = [path for path in state_history_dir.iterdir() if path.is_dir()]
    run_directories.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    stale_run_ids: set[str] = set()

    if keep_runs is not None:
        if keep_runs <= 0:
            stale_run_ids.update(path.name for path in run_directories)
        else:
            stale_run_ids.update(path.name for path in run_directories[keep_runs:])

    if max_age_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        for path in run_directories:
            modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            if modified_at < cutoff:
                stale_run_ids.add(path.name)

    for run_id in stale_run_ids:
        for stale_dir in [output_dir / "history" / run_id, reports_dir / "history" / run_id, state_dir / "runs" / run_id]:
            if stale_dir.exists():
                shutil.rmtree(stale_dir)


def run_batch_pipeline(
    *,
    source_path: Path | None = None,
    output_dir: Path | None = None,
    reports_dir: Path | None = None,
    state_dir: Path | None = None,
    date_col: str | None = None,
    sales_col: str | None = None,
    dimension_col: str | None = None,
    period: str | None = None,
) -> BatchPipelineResult:
    paths = get_project_paths()
    runtime = get_runtime_config()
    started_at = datetime.now(timezone.utc)
    resolved_output_dir = output_dir or paths.processed_data_dir
    resolved_reports_dir = reports_dir or paths.reports_dir
    resolved_state_dir = state_dir or paths.pipeline_state_dir
    resolved_date_col = date_col or runtime.default_date_col
    resolved_sales_col = sales_col or runtime.default_sales_col
    resolved_dimension_col = dimension_col if dimension_col is not None else runtime.default_dimension_col
    resolved_period = period or runtime.default_period

    try:
        loaded = load_sales_dataset(source_path)
        run_id = f"{runtime.pipeline_name}-{loaded.fingerprint[:12]}"

        LOGGER.info(
            "Executando batch pipeline | run_id=%s | source=%s | fingerprint=%s",
            run_id,
            loaded.source_path,
            loaded.fingerprint,
        )
        analysis = run_sales_analysis(
            df=loaded.dataframe,
            date_col=resolved_date_col,
            sales_col=resolved_sales_col,
            dimension_col=resolved_dimension_col,
            period=resolved_period,
            freshness_reference_date=runtime.freshness_reference_date,
            freshness_max_age_days=runtime.freshness_max_age_days,
        )

        artifact_files = generate_processed_artifacts(loaded.dataframe, resolved_output_dir)
        summary_path = export_executive_summary(analysis, output_path=resolved_reports_dir / "executive_summary.csv")
        data_dictionary_path = export_data_dictionary(resolved_reports_dir / "data_dictionary.md")
        cleaned_path = atomic_write_csv(analysis.cleaned_data, resolved_reports_dir / "cleaned_sales.csv")
        periodic_path = atomic_write_csv(analysis.periodic_sales, resolved_reports_dir / "periodic_sales.csv")
        yoy_path = atomic_write_csv(analysis.yoy_sales, resolved_reports_dir / "yoy_sales.csv")
        pareto_path = atomic_write_csv(analysis.pareto_sales, resolved_reports_dir / "pareto_sales.csv")

        quality_report_path = atomic_write_json(
            analysis.quality_report.to_dict(),
            resolved_state_dir / "quality_report.json",
        )
        kpis_path = atomic_write_json(analysis.kpis.to_dict(), resolved_state_dir / "kpis.json")
        quality_payload = analysis.quality_report.to_dict()
        kpis_payload = analysis.kpis.to_dict()
        manifest_payload = {
            "status": "success",
            "run_id": run_id,
            "pipeline_name": runtime.pipeline_name,
            "environment": runtime.environment,
            "source_path": str(loaded.source_path),
            "dataset_fingerprint": loaded.fingerprint,
            "source_size_bytes": loaded.source_size_bytes,
            "date_col": resolved_date_col,
            "sales_col": resolved_sales_col,
            "dimension_col": resolved_dimension_col,
            "period": resolved_period,
            "freshness_reference_date": runtime.freshness_reference_date.isoformat() if runtime.freshness_reference_date else None,
            "freshness_max_age_days": runtime.freshness_max_age_days,
            "started_at_utc": started_at.isoformat(),
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "quality": quality_payload,
            "kpis": kpis_payload,
            "outputs": {
                "artifacts": [str(path) for path in artifact_files],
                "reports": [
                    str(summary_path),
                    str(data_dictionary_path),
                    str(cleaned_path),
                    str(periodic_path),
                    str(yoy_path),
                    str(pareto_path),
                ],
            },
        }
        if runtime.enable_snapshots:
            manifest_payload["snapshots"] = _snapshot_run_outputs(
                run_id=run_id,
                output_dir=resolved_output_dir,
                reports_dir=resolved_reports_dir,
                state_dir=resolved_state_dir,
                cleaned_data=analysis.cleaned_data,
                periodic_sales=analysis.periodic_sales,
                yoy_sales=analysis.yoy_sales,
                pareto_sales=analysis.pareto_sales,
                quality_payload=quality_payload,
                kpis_payload=kpis_payload,
                manifest_payload=manifest_payload,
                artifact_files=artifact_files,
            )
        manifest_path = atomic_write_json(manifest_payload, resolved_state_dir / "pipeline_manifest.json")
        if runtime.enable_snapshots and (
            runtime.snapshot_retention_runs is not None or runtime.snapshot_retention_days is not None
        ):
            _apply_snapshot_retention(
                output_dir=resolved_output_dir,
                reports_dir=resolved_reports_dir,
                state_dir=resolved_state_dir,
                keep_runs=runtime.snapshot_retention_runs,
                max_age_days=runtime.snapshot_retention_days,
            )
        atomic_write_json(
            {
                "status": "success",
                "run_id": run_id,
                "dataset_fingerprint": loaded.fingerprint,
                "finished_at_utc": manifest_payload["finished_at_utc"],
                "manifest_path": str(manifest_path),
            },
            resolved_state_dir / "latest_success.json",
        )
        output_files = tuple(
            artifact_files + [summary_path, data_dictionary_path, cleaned_path, periodic_path, yoy_path, pareto_path, manifest_path]
        )
        LOGGER.info("Batch pipeline concluido | run_id=%s | arquivos=%s", run_id, len(output_files))
        return BatchPipelineResult(
            run_id=run_id,
            manifest_path=manifest_path,
            quality_report_path=quality_report_path,
            kpis_path=kpis_path,
            output_files=output_files,
        )
    except (SalesAnalyticsError, ValueError, FileNotFoundError) as exc:
        failure_path = _write_failure_state(
            state_dir=resolved_state_dir,
            runtime_pipeline_name=runtime.pipeline_name,
            environment=runtime.environment,
            source_path=source_path,
            error=exc,
        )
        LOGGER.error("Batch pipeline falhou | failure_manifest=%s | erro=%s", failure_path, exc)
        raise
