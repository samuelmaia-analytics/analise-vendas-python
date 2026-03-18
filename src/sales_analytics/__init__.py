"""Sales analytics domain package."""

from .artifacts import generate_processed_artifacts
from .batch_pipeline import BatchPipelineResult, run_batch_pipeline
from .data_dictionary import build_data_dictionary_markdown, export_data_dictionary
from .data_contract import (
    ARTIFACT_COLUMN_METADATA,
    REQUIRED_ARTIFACT_COLUMNS,
    REQUIRED_RAW_COLUMNS,
    RAW_COLUMN_METADATA,
    load_raw_sales,
    validate_processed_schema,
    validate_raw_schema,
)
from .exceptions import DataQualityError, SalesAnalyticsError
from .metrics import SalesKpis, compute_growth_over_period, compute_main_metrics, compute_pareto, compute_sales_kpis, compute_yoy
from .pipeline import SalesAnalysisResult, run_sales_analysis
from .quality import DataQualityReport, validate_sales_data
from .reporting import build_executive_summary_frame, export_executive_summary
from .settings import AppSettings, get_app_settings

__all__ = [
    "ARTIFACT_COLUMN_METADATA",
    "BatchPipelineResult",
    "REQUIRED_ARTIFACT_COLUMNS",
    "REQUIRED_RAW_COLUMNS",
    "RAW_COLUMN_METADATA",
    "DataQualityError",
    "DataQualityReport",
    "SalesAnalysisResult",
    "SalesAnalyticsError",
    "SalesKpis",
    "compute_pareto",
    "compute_sales_kpis",
    "compute_yoy",
    "compute_growth_over_period",
    "compute_main_metrics",
    "build_data_dictionary_markdown",
    "build_executive_summary_frame",
    "export_data_dictionary",
    "export_executive_summary",
    "generate_processed_artifacts",
    "get_app_settings",
    "load_raw_sales",
    "run_batch_pipeline",
    "run_sales_analysis",
    "validate_sales_data",
    "validate_processed_schema",
    "validate_raw_schema",
    "AppSettings",
]

__version__ = "0.3.0"
