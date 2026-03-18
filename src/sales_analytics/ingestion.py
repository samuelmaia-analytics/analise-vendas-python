from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import get_project_paths
from .data_contract import load_raw_sales, resolve_first_existing_path


@dataclass(frozen=True)
class LoadedDataset:
    dataframe: pd.DataFrame
    source_path: Path
    fingerprint: str
    source_size_bytes: int


def resolve_raw_sales_path(path: Path | None = None) -> Path:
    if path is not None:
        return path
    paths = get_project_paths()
    return resolve_first_existing_path(
        paths.raw_data_dir / "sales_data_sample.csv",
        paths.legacy_raw_data_dir / "sales_data_sample.csv",
    )


def compute_file_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_pointer:
        for chunk in iter(lambda: file_pointer.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_sales_dataset(path: Path | None = None) -> LoadedDataset:
    source_path = resolve_raw_sales_path(path)
    dataframe = load_raw_sales(source_path)
    return LoadedDataset(
        dataframe=dataframe,
        source_path=source_path,
        fingerprint=compute_file_fingerprint(source_path),
        source_size_bytes=source_path.stat().st_size,
    )
