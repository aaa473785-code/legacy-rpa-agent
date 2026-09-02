from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def write_action_log(log_path: Path, action: str, detail: dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "action": action,
        "detail": detail,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_action_log(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.exists():
        return []

    rows: list[dict[str, Any]] = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"raw": line})
    return rows
