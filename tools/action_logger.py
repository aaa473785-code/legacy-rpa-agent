from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
from typing import Any, Dict


def append_action_log(
    *,
    tool: str,
    action: str,
    status: str,
    detail: Dict[str, Any] | str,
    log_dir: str = "logs",
) -> Path:
    """Append one JSONL action log record.

    監査用に、AIが呼んだ外部操作ツールの履歴を残す。
    実業務化する場合はユーザーID、案件ID、承認IDなどをここに足す。
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    path = Path(log_dir) / "actions.jsonl"
    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "tool": tool,
        "action": action,
        "status": status,
        "detail": detail,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def read_action_log(log_dir: str = "logs", limit: int = 200) -> list[dict[str, Any]]:
    path = Path(log_dir) / "actions.jsonl"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"raw": line})
    return rows
