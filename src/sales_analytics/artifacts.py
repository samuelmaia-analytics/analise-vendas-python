from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data_contract import REQUIRED_RAW_COLUMNS
from .io_utils import atomic_write_csv
from .logging_utils import get_logger
from .quality import validate_sales_data
from .transformations import prepare_sales_data

LOGGER = get_logger(__name__)


def build_processed_artifact_frames(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    quality_report = validate_sales_data(
        df,
        date_col="ORDERDATE",
        sales_col="SALES",
        required_columns=REQUIRED_RAW_COLUMNS,
    )
    if quality_report.missing_required_columns:
        missing = ", ".join(quality_report.missing_required_columns)
        raise ValueError(f"Dados de entrada sem colunas obrigatorias: {missing}")

    tmp = prepare_sales_data(
        df,
        date_col="ORDERDATE",
        sales_col="SALES",
        quality_report=quality_report,
    ).rename(columns={"analysis_date": "ORDERDATE", "analysis_sales": "SALES"})
    tmp["DATE_ID"] = tmp["ORDERDATE"].dt.strftime("%Y%m%d").astype(int)
    tmp["PRODUCT_ID"] = tmp["PRODUCTCODE"].astype(str)
    tmp["CUSTOMER_ID"] = tmp["CUSTOMERNAME"].astype(str)

    fato = tmp[
        [
            "ORDERNUMBER",
            "ORDERLINENUMBER",
            "ORDERDATE",
            "DATE_ID",
            "PRODUCT_ID",
            "CUSTOMER_ID",
            "QUANTITYORDERED",
            "PRICEEACH",
            "SALES",
            "STATUS",
            "DEALSIZE",
        ]
    ].copy().sort_values(["ORDERNUMBER", "ORDERLINENUMBER"]).reset_index(drop=True)

    dim_tempo = (
        tmp[["DATE_ID", "ORDERDATE"]]
        .dropna()
        .drop_duplicates()
        .rename(columns={"ORDERDATE": "DATA"})
        .sort_values("DATA")
        .reset_index(drop=True)
    )
    dim_tempo["ANO"] = dim_tempo["DATA"].dt.year
    dim_tempo["TRIMESTRE"] = dim_tempo["DATA"].dt.quarter
    dim_tempo["MES"] = dim_tempo["DATA"].dt.month
    dim_tempo["MES_NOME"] = dim_tempo["DATA"].dt.strftime("%B")

    dim_produtos = (
        tmp[["PRODUCT_ID", "PRODUCTLINE", "PRODUCTCODE", "MSRP"]]
        .drop_duplicates(subset=["PRODUCT_ID"])
        .sort_values("PRODUCT_ID")
        .reset_index(drop=True)
    )
    dim_clientes = (
        tmp[["CUSTOMER_ID", "CUSTOMERNAME", "PHONE", "CITY", "STATE", "COUNTRY", "TERRITORY"]]
        .drop_duplicates(subset=["CUSTOMER_ID"])
        .sort_values("CUSTOMER_ID")
        .reset_index(drop=True)
    )

    return {
        "fato_vendas.csv": fato,
        "dim_tempo.csv": dim_tempo,
        "dim_produtos.csv": dim_produtos,
        "dim_clientes.csv": dim_clientes,
    }


def generate_processed_artifacts(df: pd.DataFrame, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    LOGGER.info("Gerando artefatos processados em %s", output_dir)
    frames = build_processed_artifact_frames(df)
    arquivos: list[Path] = []
    for file_name, frame in frames.items():
        arquivos.append(atomic_write_csv(frame, output_dir / file_name))
    LOGGER.info("Artefatos gerados: %s", ", ".join(str(path.name) for path in arquivos))
    return arquivos
