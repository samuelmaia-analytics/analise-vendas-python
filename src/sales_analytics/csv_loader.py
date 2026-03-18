from __future__ import annotations

import csv as csvlib
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import pandas as pd


DEFAULT_ENCODINGS = ("utf-8-sig", "utf-8", "latin-1", "ISO-8859-1", "cp1252")
DEFAULT_SEPARATORS = (",", ";", "\t", "|")


@dataclass(frozen=True)
class CsvLoadResult:
    dataframe: pd.DataFrame
    encoding: str
    separator: str


def _detect_separator(sample_text: str) -> str:
    try:
        return csvlib.Sniffer().sniff(sample_text, delimiters="".join(DEFAULT_SEPARATORS)).delimiter
    except csvlib.Error:
        separator = max(DEFAULT_SEPARATORS, key=sample_text.count)
        return separator if sample_text.count(separator) > 0 else ","


def load_csv_from_bytes(
    file_bytes: bytes,
    *,
    min_columns: int = 2,
    encodings: tuple[str, ...] = DEFAULT_ENCODINGS,
    separators: tuple[str, ...] = DEFAULT_SEPARATORS,
) -> CsvLoadResult:
    sample = file_bytes[:200_000]
    last_error: Exception | None = None

    for encoding in encodings:
        try:
            sample_text = sample.decode(encoding)
        except UnicodeDecodeError:
            continue

        separator = _detect_separator(sample_text)
        try:
            dataframe = pd.read_csv(
                BytesIO(file_bytes),
                encoding=encoding,
                sep=separator,
                low_memory=False,
                on_bad_lines="skip",
            )
            if dataframe.shape[1] >= min_columns:
                return CsvLoadResult(dataframe=dataframe, encoding=encoding, separator=separator)
        except Exception as exc:
            last_error = exc

    for encoding in encodings:
        for separator in separators:
            try:
                dataframe = pd.read_csv(
                    BytesIO(file_bytes),
                    encoding=encoding,
                    sep=separator,
                    low_memory=False,
                    on_bad_lines="skip",
                )
                if dataframe.shape[1] >= min_columns:
                    return CsvLoadResult(dataframe=dataframe, encoding=encoding, separator=separator)
            except Exception as exc:
                last_error = exc

    raise ValueError(f"Nao foi possivel ler o CSV informado. Erro: {last_error}")


def load_csv_from_path(path: Path, *, min_columns: int = 2) -> CsvLoadResult:
    return load_csv_from_bytes(path.read_bytes(), min_columns=min_columns)
