from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .env import load_project_env


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    environment: str
    raw_data_dir: Path
    processed_data_dir: Path
    legacy_raw_data_dir: Path
    legacy_processed_data_dir: Path
    reports_dir: Path
    pipeline_state_dir: Path


@dataclass(frozen=True)
class RuntimeConfig:
    environment: str
    pipeline_name: str
    log_level: str
    default_date_col: str
    default_sales_col: str
    default_dimension_col: str
    default_period: str
    enable_snapshots: bool
    snapshot_retention_runs: int | None
    snapshot_retention_days: int | None
    freshness_max_age_days: int | None
    freshness_reference_date: date | None


def project_root() -> Path:
    root = Path(__file__).resolve().parents[2]
    load_project_env(root / ".env")
    return root


def _read_path_override(env_name: str, default: Path) -> Path:
    raw_value = os.getenv(env_name)
    if raw_value is None or raw_value.strip() == "":
        return default
    return Path(raw_value).expanduser()


def _read_bool(env_name: str, default: bool) -> bool:
    raw_value = os.getenv(env_name)
    if raw_value is None or raw_value.strip() == "":
        return default
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"{env_name} must be a boolean-like value")


def _read_optional_non_negative_int(env_name: str) -> int | None:
    raw_value = os.getenv(env_name)
    if raw_value is None or raw_value.strip() == "":
        return None
    value = int(raw_value)
    if value < 0:
        raise ValueError(f"{env_name} must be zero or greater")
    return value


def _read_optional_date(env_name: str) -> date | None:
    raw_value = os.getenv(env_name)
    if raw_value is None or raw_value.strip() == "":
        return None
    return date.fromisoformat(raw_value.strip())


def get_project_paths() -> ProjectPaths:
    root = project_root()
    environment = os.getenv("APP_ENV", "local").strip() or "local"
    return ProjectPaths(
        root=root,
        environment=environment,
        raw_data_dir=_read_path_override("RAW_DATA_DIR", root / "data" / "raw"),
        processed_data_dir=_read_path_override("PROCESSED_DATA_DIR", root / "data" / "processed"),
        legacy_raw_data_dir=root / "legacy" / "dados",
        legacy_processed_data_dir=root / "legacy" / "dados_processados",
        reports_dir=_read_path_override("REPORTS_DIR", root / "reports"),
        pipeline_state_dir=_read_path_override("PIPELINE_STATE_DIR", root / "data" / "state"),
    )


def get_runtime_config() -> RuntimeConfig:
    project_root()
    return RuntimeConfig(
        environment=os.getenv("APP_ENV", "local").strip() or "local",
        pipeline_name=os.getenv("PIPELINE_NAME", "sales-analytics").strip() or "sales-analytics",
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper() or "INFO",
        default_date_col=os.getenv("ANALYSIS_DATE_COL", "ORDERDATE").strip() or "ORDERDATE",
        default_sales_col=os.getenv("ANALYSIS_SALES_COL", "SALES").strip() or "SALES",
        default_dimension_col=os.getenv("ANALYSIS_DIMENSION_COL", "PRODUCTLINE").strip() or "PRODUCTLINE",
        default_period=os.getenv("ANALYSIS_PERIOD", "M").strip().upper() or "M",
        enable_snapshots=_read_bool("ENABLE_PIPELINE_SNAPSHOTS", True),
        snapshot_retention_runs=_read_optional_non_negative_int("SNAPSHOT_RETENTION_RUNS"),
        snapshot_retention_days=_read_optional_non_negative_int("SNAPSHOT_RETENTION_DAYS"),
        freshness_max_age_days=_read_optional_non_negative_int("DATA_FRESHNESS_MAX_AGE_DAYS"),
        freshness_reference_date=_read_optional_date("DATA_FRESHNESS_REFERENCE_DATE"),
    )
