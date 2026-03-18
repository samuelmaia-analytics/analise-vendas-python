from __future__ import annotations

from pathlib import Path

import pytest

from src.sales_analytics.csv_loader import load_csv_from_bytes, load_csv_from_path


def test_load_csv_from_bytes_detects_semicolon_separator():
    payload = "ORDERDATE;SALES\n2024-01-01;100\n".encode("utf-8")

    loaded = load_csv_from_bytes(payload)

    assert loaded.separator == ";"
    assert loaded.encoding in {"utf-8-sig", "utf-8"}
    assert list(loaded.dataframe.columns) == ["ORDERDATE", "SALES"]


def test_load_csv_from_path_reads_latin1_file(tmp_path: Path):
    path = tmp_path / "sales.csv"
    path.write_bytes("ORDERDATE,SALES,CITY\n2024-01-01,100,São Paulo\n".encode("latin-1"))

    loaded = load_csv_from_path(path)

    assert "CITY" in loaded.dataframe.columns
    assert loaded.dataframe.loc[0, "CITY"] == "São Paulo"


def test_load_csv_from_bytes_raises_for_invalid_payload():
    with pytest.raises(ValueError, match="Nao foi possivel ler o CSV informado"):
        load_csv_from_bytes(b"\x00\x01\x02")
