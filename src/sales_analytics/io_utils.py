from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd


def _atomic_write(target: Path, write_fn: Any) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temp_path_raw = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    os.close(file_descriptor)
    temp_path = Path(temp_path_raw)
    try:
        write_fn(temp_path)
        os.replace(temp_path, target)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise
    return target


def atomic_write_csv(df: pd.DataFrame, target: Path, *, encoding: str = "utf-8") -> Path:
    return _atomic_write(target, lambda tmp: df.to_csv(tmp, index=False, encoding=encoding))


def atomic_write_json(payload: dict[str, Any], target: Path) -> Path:
    return _atomic_write(
        target,
        lambda tmp: tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True), encoding="utf-8"),
    )
