from __future__ import annotations

from datetime import datetime


def dry_run_browser_action(keyword: str) -> dict:
    return {
        "mode": "dry_run",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "steps": [
            "サンプルWeb画面を開く",
            f"顧客名に「{keyword}」を入力する",
            "検索ボタンを押す",
            "結果件数を確認する",
            "CSV出力ボタンを押す",
            "出力CSVを確認する",
        ],
        "note": "DRY RUNのため実際の画面操作は行っていません。",
    }
