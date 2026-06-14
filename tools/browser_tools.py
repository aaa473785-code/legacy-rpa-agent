from __future__ import annotations

from .action_logger import append_action_log


def dry_run_browser_action(action: str, target: str) -> str:
    """Dry-run placeholder used before real Playwright/pywinauto execution."""
    message = f"DRY RUN: {target} に対して {action} を実行予定"
    append_action_log(
        tool="dry_run",
        action=action,
        status="planned",
        detail={"target": target, "message": message},
    )
    return message
