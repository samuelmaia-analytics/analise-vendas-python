from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .artifacts import generate_processed_artifacts
from .batch_pipeline import BatchPipelineResult, run_batch_pipeline
from .config import RuntimeConfig, get_project_paths, get_runtime_config
from .data_dictionary import export_data_dictionary
from .data_contract import load_raw_sales
from .exceptions import SalesAnalyticsError
from .logging_utils import get_logger
from .pipeline import run_sales_analysis
from .reporting import export_executive_summary

LOGGER = get_logger(__name__)


def _add_analysis_arguments(parser: argparse.ArgumentParser, runtime: RuntimeConfig) -> None:
    parser.add_argument("--input", default=None)
    parser.add_argument("--date-col", default=runtime.default_date_col)
    parser.add_argument("--sales-col", default=runtime.default_sales_col)
    parser.add_argument("--dimension-col", default=runtime.default_dimension_col)
    parser.add_argument("--period", default=runtime.default_period, choices=["M", "T", "A"])


def build_parser() -> argparse.ArgumentParser:
    runtime = get_runtime_config()
    parser = argparse.ArgumentParser(description="Official CLI for the sales analytics project.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary_parser = subparsers.add_parser("summary", help="Generate an executive summary from the raw dataset.")
    _add_analysis_arguments(summary_parser, runtime)

    export_parser = subparsers.add_parser("export-summary", help="Export an executive summary CSV to the reports folder.")
    _add_analysis_arguments(export_parser, runtime)
    export_parser.add_argument("--output", default=None)

    growth_parser = subparsers.add_parser("growth", help="Compute growth over time from the raw dataset.")
    _add_analysis_arguments(growth_parser, runtime)

    artifact_parser = subparsers.add_parser("build-artifacts", help="Generate processed artifacts from the raw dataset.")
    artifact_parser.add_argument("--input", default=None)
    artifact_parser.add_argument("--output-dir", default=None)

    dictionary_parser = subparsers.add_parser("generate-data-dictionary", help="Generate a markdown data dictionary from data contracts.")
    dictionary_parser.add_argument("--output", default=None)

    pipeline_parser = subparsers.add_parser("run-pipeline", help="Run the full batch pipeline and persist outputs.")
    _add_analysis_arguments(pipeline_parser, runtime)
    pipeline_parser.add_argument("--output-dir", default=None)
    pipeline_parser.add_argument("--reports-dir", default=None)
    pipeline_parser.add_argument("--state-dir", default=None)

    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        input_path = None if getattr(args, "input", None) is None else Path(args.input)
        df: pd.DataFrame | None = None if args.command == "run-pipeline" else load_raw_sales(input_path)

        if args.command == "summary":
            assert df is not None
            result = run_sales_analysis(
                df=df,
                date_col=args.date_col,
                sales_col=args.sales_col,
                dimension_col=args.dimension_col,
                period=args.period,
            )
            print(f"receita_total,{result.kpis.total_revenue:.2f}")
            print(f"pedidos,{result.kpis.total_orders}")
            print(f"ticket_medio,{result.kpis.average_order_value:.2f}")
            print(f"crescimento_medio_pct,{result.kpis.average_growth_pct:.2f}")
            print(f"melhor_periodo,{result.kpis.best_period}")
            print(f"pior_periodo,{result.kpis.worst_period}")
            if result.kpis.top3_share_pct is not None:
                print(f"top3_share_pct,{result.kpis.top3_share_pct:.2f}")
            return 0

        if args.command == "growth":
            assert df is not None
            result = run_sales_analysis(
                df=df,
                date_col=args.date_col,
                sales_col=args.sales_col,
                dimension_col=None,
                period=args.period,
            )
            print(result.periodic_sales.to_csv(index=False))
            return 0

        if args.command == "export-summary":
            assert df is not None
            result = run_sales_analysis(
                df=df,
                date_col=args.date_col,
                sales_col=args.sales_col,
                dimension_col=args.dimension_col,
                period=args.period,
            )
            output_path = None if args.output is None else Path(args.output)
            exported = export_executive_summary(result, output_path=output_path)
            print(exported)
            return 0

        if args.command == "build-artifacts":
            assert df is not None
            default_output = get_project_paths().processed_data_dir
            output_dir = default_output if args.output_dir is None else Path(args.output_dir)
            files = generate_processed_artifacts(df=df, output_dir=output_dir)
            for file_path in files:
                print(file_path)
            return 0

        if args.command == "generate-data-dictionary":
            default_output = get_project_paths().reports_dir / "data_dictionary.md"
            exported = export_data_dictionary(default_output if args.output is None else Path(args.output))
            print(exported)
            return 0

        if args.command == "run-pipeline":
            pipeline_result: BatchPipelineResult = run_batch_pipeline(
                source_path=input_path,
                output_dir=None if args.output_dir is None else Path(args.output_dir),
                reports_dir=None if args.reports_dir is None else Path(args.reports_dir),
                state_dir=None if args.state_dir is None else Path(args.state_dir),
                date_col=args.date_col,
                sales_col=args.sales_col,
                dimension_col=args.dimension_col,
                period=args.period,
            )
            print(f"run_id,{pipeline_result.run_id}")
            print(f"manifest,{pipeline_result.manifest_path}")
            for file_path in pipeline_result.output_files:
                print(file_path)
            return 0
    except (SalesAnalyticsError, ValueError, FileNotFoundError) as exc:
        LOGGER.error("Falha na execucao da CLI: %s", exc)
        print(f"Erro: {exc}")
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
