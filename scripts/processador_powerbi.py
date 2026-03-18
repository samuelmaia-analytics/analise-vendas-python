from __future__ import annotations

from pathlib import Path

from src.sales_analytics.batch_pipeline import run_batch_pipeline
from src.sales_analytics.config import get_project_paths


def main() -> int:
    paths = get_project_paths()
    result = run_batch_pipeline(
        output_dir=paths.processed_data_dir,
        reports_dir=paths.reports_dir,
        state_dir=paths.pipeline_state_dir,
    )
    print(f"Pipeline executado com sucesso: {result.run_id}")
    print(f"Manifesto: {result.manifest_path}")
    for file_path in result.output_files:
        relative = Path(file_path).resolve().relative_to(paths.root.resolve())
        print(relative)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
