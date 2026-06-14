from __future__ import annotations

from datetime import datetime
from pathlib import Path


def save_markdown_report(content: str, output_dir: str = "logs") -> Path:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / f"report_{ts}.md"
    path.write_text(content, encoding="utf-8")
    return path
