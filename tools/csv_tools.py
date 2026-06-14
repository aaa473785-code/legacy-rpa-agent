from __future__ import annotations

from pathlib import Path
import pandas as pd


def read_csv_preview(path: str, max_rows: int = 20) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSVが見つかりません: {csv_path}")
    return pd.read_csv(csv_path).head(max_rows)
