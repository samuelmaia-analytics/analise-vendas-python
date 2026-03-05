from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_RAW_COLUMNS = {
    "ORDERNUMBER",
    "ORDERDATE",
    "SALES",
    "PRODUCTLINE",
    "CUSTOMERNAME",
    "COUNTRY",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_raw_sales(path: Path | None = None) -> pd.DataFrame:
    csv_path = path or (project_root() / "data" / "raw" / "sales_data_sample.csv")
    return pd.read_csv(csv_path, encoding="latin-1")


def validate_raw_schema(df: pd.DataFrame) -> tuple[bool, list[str]]:
    missing = sorted(REQUIRED_RAW_COLUMNS - set(df.columns))
    return len(missing) == 0, missing
