from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import get_project_paths
from .csv_loader import load_csv_from_path
from .logging_utils import get_logger

LOGGER = get_logger(__name__)

RAW_COLUMN_METADATA = {
    "ORDERNUMBER": {"definition": "Unique order identifier", "type": "integer", "quality_rule": "Not null"},
    "ORDERLINENUMBER": {"definition": "Line item number inside the order", "type": "integer", "quality_rule": "Not null and > 0"},
    "ORDERDATE": {"definition": "Transaction date", "type": "datetime", "quality_rule": "Convertible to datetime"},
    "QUANTITYORDERED": {"definition": "Quantity ordered in the line item", "type": "integer", "quality_rule": ">= 1"},
    "PRICEEACH": {"definition": "Unit price", "type": "numeric", "quality_rule": ">= 0"},
    "SALES": {"definition": "Revenue amount for the line item", "type": "numeric", "quality_rule": "Not null and >= 0"},
    "STATUS": {"definition": "Order status", "type": "string", "quality_rule": "Controlled business status"},
    "DEALSIZE": {"definition": "Deal size band", "type": "string", "quality_rule": "Controlled business category"},
    "PRODUCTLINE": {"definition": "Product category line", "type": "string", "quality_rule": "Not null"},
    "PRODUCTCODE": {"definition": "Unique product code", "type": "string", "quality_rule": "Not null"},
    "MSRP": {"definition": "Manufacturer suggested retail price", "type": "numeric", "quality_rule": ">= 0"},
    "CUSTOMERNAME": {"definition": "Customer name", "type": "string", "quality_rule": "Not null"},
    "PHONE": {"definition": "Customer phone number", "type": "string", "quality_rule": "Nullable contact field"},
    "CITY": {"definition": "Customer city", "type": "string", "quality_rule": "Nullable geography field"},
    "STATE": {"definition": "Customer state", "type": "string", "quality_rule": "Nullable geography field"},
    "COUNTRY": {"definition": "Customer country", "type": "string", "quality_rule": "Not null"},
    "TERRITORY": {"definition": "Commercial territory", "type": "string", "quality_rule": "Nullable geography field"},
}

REQUIRED_RAW_COLUMNS = {
    "ORDERNUMBER",
    "ORDERLINENUMBER",
    "ORDERDATE",
    "QUANTITYORDERED",
    "PRICEEACH",
    "SALES",
    "STATUS",
    "DEALSIZE",
    "PRODUCTLINE",
    "PRODUCTCODE",
    "MSRP",
    "CUSTOMERNAME",
    "PHONE",
    "CITY",
    "STATE",
    "COUNTRY",
    "TERRITORY",
}

REQUIRED_ARTIFACT_COLUMNS = {
    "fato_vendas.csv": {
        "ORDERNUMBER",
        "ORDERLINENUMBER",
        "ORDERDATE",
        "DATE_ID",
        "PRODUCT_ID",
        "CUSTOMER_ID",
        "QUANTITYORDERED",
        "PRICEEACH",
        "SALES",
    },
    "dim_tempo.csv": {"DATE_ID", "DATA", "ANO", "TRIMESTRE", "MES", "MES_NOME"},
    "dim_produtos.csv": {"PRODUCT_ID", "PRODUCTLINE", "PRODUCTCODE", "MSRP"},
    "dim_clientes.csv": {"CUSTOMER_ID", "CUSTOMERNAME", "PHONE", "CITY", "STATE", "COUNTRY", "TERRITORY"},
}

ARTIFACT_COLUMN_METADATA = {
    "fato_vendas.csv": {
        "ORDERNUMBER": {"definition": "Order identifier", "type": "integer", "quality_rule": "Not null"},
        "ORDERLINENUMBER": {"definition": "Order line item", "type": "integer", "quality_rule": "Not null"},
        "ORDERDATE": {"definition": "Original transaction date", "type": "datetime", "quality_rule": "Not null"},
        "DATE_ID": {"definition": "Date surrogate key in YYYYMMDD format", "type": "integer", "quality_rule": "Not null"},
        "PRODUCT_ID": {"definition": "Product business key", "type": "string", "quality_rule": "Not null"},
        "CUSTOMER_ID": {"definition": "Customer business key", "type": "string", "quality_rule": "Not null"},
        "QUANTITYORDERED": {"definition": "Quantity ordered", "type": "integer", "quality_rule": ">= 1"},
        "PRICEEACH": {"definition": "Unit price", "type": "numeric", "quality_rule": ">= 0"},
        "SALES": {"definition": "Revenue amount", "type": "numeric", "quality_rule": ">= 0"},
    },
    "dim_tempo.csv": {
        "DATE_ID": {"definition": "Date surrogate key in YYYYMMDD format", "type": "integer", "quality_rule": "Unique"},
        "DATA": {"definition": "Calendar date", "type": "datetime", "quality_rule": "Unique"},
        "ANO": {"definition": "Calendar year", "type": "integer", "quality_rule": "Derived from DATA"},
        "TRIMESTRE": {"definition": "Calendar quarter", "type": "integer", "quality_rule": "Derived from DATA"},
        "MES": {"definition": "Calendar month number", "type": "integer", "quality_rule": "Derived from DATA"},
        "MES_NOME": {"definition": "Calendar month label", "type": "string", "quality_rule": "Derived from DATA"},
    },
    "dim_produtos.csv": {
        "PRODUCT_ID": {"definition": "Product business key", "type": "string", "quality_rule": "Unique"},
        "PRODUCTLINE": {"definition": "Product category line", "type": "string", "quality_rule": "Not null"},
        "PRODUCTCODE": {"definition": "Original product code", "type": "string", "quality_rule": "Not null"},
        "MSRP": {"definition": "Manufacturer suggested retail price", "type": "numeric", "quality_rule": ">= 0"},
    },
    "dim_clientes.csv": {
        "CUSTOMER_ID": {"definition": "Customer business key", "type": "string", "quality_rule": "Unique"},
        "CUSTOMERNAME": {"definition": "Customer name", "type": "string", "quality_rule": "Not null"},
        "PHONE": {"definition": "Customer phone number", "type": "string", "quality_rule": "Nullable"},
        "CITY": {"definition": "Customer city", "type": "string", "quality_rule": "Nullable"},
        "STATE": {"definition": "Customer state", "type": "string", "quality_rule": "Nullable"},
        "COUNTRY": {"definition": "Customer country", "type": "string", "quality_rule": "Not null"},
        "TERRITORY": {"definition": "Commercial territory", "type": "string", "quality_rule": "Nullable"},
    },
}


def resolve_first_existing_path(*candidates: Path) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    checked = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Nenhum arquivo encontrado nos caminhos esperados: {checked}")


def load_raw_sales(path: Path | None = None) -> pd.DataFrame:
    if path is not None:
        csv_path = path
    else:
        paths = get_project_paths()
        csv_path = resolve_first_existing_path(
            paths.raw_data_dir / "sales_data_sample.csv",
            paths.legacy_raw_data_dir / "sales_data_sample.csv",
        )
    LOGGER.info("Carregando base bruta de vendas: %s", csv_path)
    loaded = load_csv_from_path(csv_path)
    LOGGER.info("Base carregada | encoding=%s | separator=%s | linhas=%s", loaded.encoding, loaded.separator, len(loaded.dataframe))
    return loaded.dataframe


def validate_raw_schema(df: pd.DataFrame) -> tuple[bool, list[str]]:
    missing = sorted(REQUIRED_RAW_COLUMNS - set(df.columns))
    return len(missing) == 0, missing


def validate_processed_schema(file_name: str, df: pd.DataFrame) -> tuple[bool, list[str]]:
    expected = REQUIRED_ARTIFACT_COLUMNS.get(file_name)
    if expected is None:
        raise ValueError(f"Artefato sem contrato registrado: {file_name}")
    missing = sorted(expected - set(df.columns))
    return len(missing) == 0, missing
