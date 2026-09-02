from __future__ import annotations

from pathlib import Path
from datetime import datetime
import csv

from tools.action_logger import write_action_log


def run_sample_customer_search(base_dir: Path, keyword: str) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "playwright が入っていません。`python -m pip install -r requirements.txt` と "
            "`python -m playwright install chromium` を実行してください。"
        ) from exc

    html_path = base_dir / "sample_web" / "customers.html"
    downloads_dir = base_dir / "downloads"
    logs_dir = base_dir / "logs"
    log_path = logs_dir / "actions.jsonl"

    downloads_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = logs_dir / f"playwright_customer_search_{timestamp}.png"
    csv_path = downloads_dir / f"customers_{timestamp}.csv"

    rows = [
        {"顧客ID": "C001", "顧客名": "山田 太郎", "部署": "営業部", "注意点": ""},
        {"顧客ID": "C002", "顧客名": "山田 花子", "部署": "総務部", "注意点": "要確認"},
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(html_path.as_uri())

        page.fill("#keyword", keyword)
        page.click("#searchButton")
        page.screenshot(path=str(screenshot_path), full_page=True)

        with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["顧客ID", "顧客名", "部署", "注意点"])
            writer.writeheader()
            writer.writerows(rows)

        browser.close()

    result = {
        "keyword": keyword,
        "csv_path": str(csv_path),
        "screenshot_path": str(screenshot_path),
        "row_count": len(rows),
    }

    write_action_log(log_path, "playwright_sample_customer_search", result)
    return result
