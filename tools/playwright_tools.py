from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .action_logger import append_action_log


@dataclass
class BrowserRunResult:
    url: str
    keyword: str
    result_count: int
    exported_csv: str
    screenshot: str
    log_file: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _default_sample_url() -> str:
    sample = Path("sample_web/customers.html").resolve()
    if not sample.exists():
        raise FileNotFoundError("sample_web/customers.html が見つかりません。")
    return sample.as_uri()


def run_sample_customer_search(
    *,
    keyword: str = "山田",
    headless: bool = True,
    slow_mo_ms: int = 0,
    url: str | None = None,
    download_dir: str = "downloads",
) -> BrowserRunResult:
    """Run a safe Playwright demo against the bundled sample web page.

    - 顧客検索画面を開く
    - 検索語を入力
    - 検索ボタンを押す
    - CSV出力ボタンを押す
    - スクリーンショットと操作ログを残す

    実業務画面に接続する場合は、url と selector 部分を置き換える。
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "playwright が未インストールです。\n"
            "python -m pip install playwright\n"
            "python -m playwright install chromium\n"
            "を実行してください。"
        ) from exc

    url = url or _default_sample_url()
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = str(Path("logs") / f"browser_{ts}.png")
    export_path = str(Path(download_dir) / f"customers_export_{ts}.csv")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo_ms)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        page.goto(url)
        page.fill("#keyword", keyword)
        page.click("#search")
        page.wait_for_selector("#results tbody tr")

        result_count_text = page.locator("#result-count").inner_text()
        result_count = int("".join(ch for ch in result_count_text if ch.isdigit()) or "0")

        with page.expect_download() as download_info:
            page.click("#export")
        download = download_info.value
        download.save_as(export_path)

        page.screenshot(path=screenshot_path, full_page=True)
        browser.close()

    log_file = append_action_log(
        tool="playwright",
        action="sample_customer_search",
        status="success",
        detail={
            "url": url,
            "keyword": keyword,
            "result_count": result_count,
            "exported_csv": export_path,
            "screenshot": screenshot_path,
        },
    )
    return BrowserRunResult(
        url=url,
        keyword=keyword,
        result_count=result_count,
        exported_csv=export_path,
        screenshot=screenshot_path,
        log_file=str(log_file),
    )


def get_page_title(*, url: str, headless: bool = True) -> str:
    """Small connectivity check for a browser target."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("playwright が未インストールです。") from exc

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url)
        title = page.title()
        browser.close()

    append_action_log(
        tool="playwright",
        action="get_page_title",
        status="success",
        detail={"url": url, "title": title},
    )
    return title
