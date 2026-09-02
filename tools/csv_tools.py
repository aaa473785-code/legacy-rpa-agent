from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_csv_preview(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"CSVが見つかりません: {path}")

    df = pd.read_csv(path, encoding="utf-8-sig")

    summary = {
        "path": str(path),
        "rows": int(len(df)),
        "columns": list(df.columns),
        "blank_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }

    return {
        "summary": summary,
        "preview": df.head(20),
    }
