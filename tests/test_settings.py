from __future__ import annotations

from datetime import date

import pytest

from src.sales_analytics.config import get_project_paths, get_runtime_config
from src.sales_analytics.settings import get_app_settings


def test_get_app_settings_reads_defaults(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("MAX_UPLOAD_MB", raising=False)
    monkeypatch.delenv("MAX_UPLOAD_ROWS", raising=False)
    monkeypatch.delenv("MAX_UPLOAD_COLUMNS", raising=False)
    monkeypatch.delenv("STREAMLIT_SERVER_PORT", raising=False)

    settings = get_app_settings()

    assert settings.max_upload_mb == 40
    assert settings.max_upload_rows == 250000
    assert settings.max_upload_columns == 50
    assert settings.streamlit_port == 8501


def test_get_app_settings_rejects_invalid_values(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MAX_UPLOAD_MB", "0")

    with pytest.raises(ValueError, match="MAX_UPLOAD_MB must be greater than zero"):
        get_app_settings()


def test_runtime_config_reads_environment(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("PIPELINE_NAME", "portfolio-pipeline")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("ENABLE_PIPELINE_SNAPSHOTS", "true")
    monkeypatch.setenv("SNAPSHOT_RETENTION_RUNS", "5")
    monkeypatch.setenv("SNAPSHOT_RETENTION_DAYS", "30")
    monkeypatch.setenv("DATA_FRESHNESS_MAX_AGE_DAYS", "14")
    monkeypatch.setenv("DATA_FRESHNESS_REFERENCE_DATE", "2024-12-31")

    runtime = get_runtime_config()

    assert runtime.environment == "test"
    assert runtime.pipeline_name == "portfolio-pipeline"
    assert runtime.log_level == "DEBUG"
    assert runtime.enable_snapshots is True
    assert runtime.snapshot_retention_runs == 5
    assert runtime.snapshot_retention_days == 30
    assert runtime.freshness_max_age_days == 14
    assert runtime.freshness_reference_date == date(2024, 12, 31)


def test_project_paths_support_overrides(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setenv("RAW_DATA_DIR", str(tmp_path / "raw"))
    monkeypatch.setenv("PROCESSED_DATA_DIR", str(tmp_path / "processed"))
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path / "reports"))
    monkeypatch.setenv("PIPELINE_STATE_DIR", str(tmp_path / "state"))

    paths = get_project_paths()

    assert paths.raw_data_dir == tmp_path / "raw"
    assert paths.processed_data_dir == tmp_path / "processed"
    assert paths.reports_dir == tmp_path / "reports"
    assert paths.pipeline_state_dir == tmp_path / "state"
