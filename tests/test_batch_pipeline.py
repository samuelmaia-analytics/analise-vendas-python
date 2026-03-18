from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pandas as pd
import pytest

from src.sales_analytics.batch_pipeline import run_batch_pipeline


def test_run_batch_pipeline_persists_idempotent_outputs(tmp_path: Path):
    output_dir = tmp_path / "processed"
    reports_dir = tmp_path / "reports"
    state_dir = tmp_path / "state"

    first_result = run_batch_pipeline(
        output_dir=output_dir,
        reports_dir=reports_dir,
        state_dir=state_dir,
    )
    second_result = run_batch_pipeline(
        output_dir=output_dir,
        reports_dir=reports_dir,
        state_dir=state_dir,
    )

    assert first_result.run_id == second_result.run_id
    assert first_result.manifest_path == second_result.manifest_path
    assert (output_dir / "fato_vendas.csv").exists()
    assert (reports_dir / "cleaned_sales.csv").exists()
    assert (state_dir / "pipeline_manifest.json").exists()

    manifest = json.loads((state_dir / "pipeline_manifest.json").read_text(encoding="utf-8"))
    assert manifest["dataset_fingerprint"]
    assert manifest["status"] == "success"
    assert manifest["quality"]["is_valid"] is True
    assert manifest["outputs"]["artifacts"]
    assert "snapshots" in manifest
    assert (output_dir / "history" / first_result.run_id / "fato_vendas.csv").exists()
    assert (reports_dir / "history" / first_result.run_id / "cleaned_sales.csv").exists()
    assert (state_dir / "runs" / first_result.run_id / "pipeline_manifest.json").exists()


def test_run_batch_pipeline_accepts_explicit_source(tmp_path: Path):
    source = tmp_path / "sales.csv"
    source.write_text(
        "\n".join(
            [
                "ORDERNUMBER,QUANTITYORDERED,PRICEEACH,ORDERLINENUMBER,SALES,ORDERDATE,STATUS,QTR_ID,MONTH_ID,YEAR_ID,PRODUCTLINE,MSRP,PRODUCTCODE,CUSTOMERNAME,PHONE,ADDRESSLINE1,ADDRESSLINE2,CITY,STATE,POSTALCODE,COUNTRY,TERRITORY,CONTACTLASTNAME,CONTACTFIRSTNAME,DEALSIZE",
                "1,2,10,1,20,2024-01-01,Shipped,1,1,2024,Classic Cars,30,S10_1,Client A,123,Street,,Sao Paulo,SP,01000,Brazil,LATAM,Silva,Ana,Small",
            ]
        ),
        encoding="utf-8",
    )

    result = run_batch_pipeline(
        source_path=source,
        output_dir=tmp_path / "processed",
        reports_dir=tmp_path / "reports",
        state_dir=tmp_path / "state",
    )

    cleaned = pd.read_csv(tmp_path / "reports" / "cleaned_sales.csv")
    assert result.run_id.startswith("sales-analytics-")
    assert len(cleaned) == 1


def test_run_batch_pipeline_persists_failure_manifest(tmp_path: Path):
    source = tmp_path / "broken.csv"
    source.write_text("ORDERDATE,SALES\ninvalid,abc\n", encoding="utf-8")

    with pytest.raises(Exception):
        run_batch_pipeline(
            source_path=source,
            output_dir=tmp_path / "processed",
            reports_dir=tmp_path / "reports",
            state_dir=tmp_path / "state",
        )

    failure_manifest = json.loads((tmp_path / "state" / "pipeline_failure.json").read_text(encoding="utf-8"))
    assert failure_manifest["status"] == "failed"
    assert failure_manifest["error_type"] in {"DataQualityError", "ValueError"}


def test_run_batch_pipeline_applies_snapshot_retention(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SNAPSHOT_RETENTION_RUNS", "1")

    first_source = tmp_path / "sales_first.csv"
    second_source = tmp_path / "sales_second.csv"
    header = (
        "ORDERNUMBER,QUANTITYORDERED,PRICEEACH,ORDERLINENUMBER,SALES,ORDERDATE,STATUS,QTR_ID,MONTH_ID,YEAR_ID,"
        "PRODUCTLINE,MSRP,PRODUCTCODE,CUSTOMERNAME,PHONE,ADDRESSLINE1,ADDRESSLINE2,CITY,STATE,POSTALCODE,COUNTRY,"
        "TERRITORY,CONTACTLASTNAME,CONTACTFIRSTNAME,DEALSIZE\n"
    )
    first_source.write_text(
        header + "1,2,10,1,20,2024-01-01,Shipped,1,1,2024,Classic Cars,30,S10_1,Client A,123,Street,,Sao Paulo,SP,01000,Brazil,LATAM,Silva,Ana,Small\n",
        encoding="utf-8",
    )
    second_source.write_text(
        header + "2,3,15,1,45,2024-02-01,Shipped,1,2,2024,Motorcycles,40,S10_2,Client B,456,Avenue,,Rio,RJ,20000,Brazil,LATAM,Souza,Bruno,Medium\n",
        encoding="utf-8",
    )

    first_result = run_batch_pipeline(
        source_path=first_source,
        output_dir=tmp_path / "processed",
        reports_dir=tmp_path / "reports",
        state_dir=tmp_path / "state",
    )
    second_result = run_batch_pipeline(
        source_path=second_source,
        output_dir=tmp_path / "processed",
        reports_dir=tmp_path / "reports",
        state_dir=tmp_path / "state",
    )

    assert not (tmp_path / "state" / "runs" / first_result.run_id).exists()
    assert (tmp_path / "state" / "runs" / second_result.run_id).exists()


def test_run_batch_pipeline_applies_snapshot_retention_by_age(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SNAPSHOT_RETENTION_DAYS", "1")

    first_source = tmp_path / "sales_first.csv"
    second_source = tmp_path / "sales_second.csv"
    header = (
        "ORDERNUMBER,QUANTITYORDERED,PRICEEACH,ORDERLINENUMBER,SALES,ORDERDATE,STATUS,QTR_ID,MONTH_ID,YEAR_ID,"
        "PRODUCTLINE,MSRP,PRODUCTCODE,CUSTOMERNAME,PHONE,ADDRESSLINE1,ADDRESSLINE2,CITY,STATE,POSTALCODE,COUNTRY,"
        "TERRITORY,CONTACTLASTNAME,CONTACTFIRSTNAME,DEALSIZE\n"
    )
    first_source.write_text(
        header + "1,2,10,1,20,2024-01-01,Shipped,1,1,2024,Classic Cars,30,S10_1,Client A,123,Street,,Sao Paulo,SP,01000,Brazil,LATAM,Silva,Ana,Small\n",
        encoding="utf-8",
    )
    second_source.write_text(
        header + "2,3,15,1,45,2024-02-01,Shipped,1,2,2024,Motorcycles,40,S10_2,Client B,456,Avenue,,Rio,RJ,20000,Brazil,LATAM,Souza,Bruno,Medium\n",
        encoding="utf-8",
    )

    result = run_batch_pipeline(
        source_path=first_source,
        output_dir=tmp_path / "processed",
        reports_dir=tmp_path / "reports",
        state_dir=tmp_path / "state",
    )

    run_state_dir = tmp_path / "state" / "runs" / result.run_id
    old_timestamp = time.time() - (3 * 24 * 60 * 60)
    os.utime(run_state_dir, (old_timestamp, old_timestamp))

    run_batch_pipeline(
        source_path=second_source,
        output_dir=tmp_path / "processed",
        reports_dir=tmp_path / "reports",
        state_dir=tmp_path / "state",
    )

    assert not run_state_dir.exists()
