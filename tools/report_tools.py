from __future__ import annotations

from pathlib import Path


def save_markdown_report(markdown_text: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown_text, encoding="utf-8")
    return path
