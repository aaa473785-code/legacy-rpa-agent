from __future__ import annotations

import os
import platform
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from .action_logger import append_action_log


@dataclass
class WindowInfo:
    title: str
    class_name: str | None = None
    control_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WindowsRunResult:
    action: str
    status: str
    window_title: str
    detail: str
    log_file: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _require_windows() -> None:
    if platform.system().lower() != "windows":
        raise RuntimeError("pywinauto デモは Windows 上で実行してください。")


def _import_pywinauto():
    _require_windows()
    try:
        from pywinauto import Desktop
        from pywinauto.application import Application
    except ImportError as exc:
        raise RuntimeError(
            "pywinauto が未インストールです。\n"
            "python -m pip install pywinauto pyperclip\n"
            "を実行してください。"
        ) from exc
    return Desktop, Application


def list_top_windows(limit: int = 20) -> list[WindowInfo]:
    """List visible top-level windows using Microsoft UI Automation backend."""
    Desktop, _ = _import_pywinauto()
    desktop = Desktop(backend="uia")
    infos: list[WindowInfo] = []
    for w in desktop.windows()[:limit]:
        try:
            title = w.window_text()
            if not title:
                continue
            infos.append(
                WindowInfo(
                    title=title,
                    class_name=getattr(w.element_info, "class_name", None),
                    control_type=getattr(w.element_info, "control_type", None),
                )
            )
        except Exception:
            continue

    append_action_log(
        tool="pywinauto",
        action="list_top_windows",
        status="success",
        detail={"count": len(infos), "titles": [i.title for i in infos]},
    )
    return infos


def run_notepad_demo(text: str = "legacy-rpa-agent pywinauto demo") -> WindowsRunResult:
    """Open Notepad and paste text. Safe Windows GUI automation demo.

    保存や送信はしない。メモ帳を開いて文字を貼り付けるだけ。
    日本語入力の安定性を上げるため、クリップボード経由で貼り付ける。
    """
    _, Application = _import_pywinauto()
    try:
        import pyperclip
    except ImportError as exc:
        raise RuntimeError("pyperclip が未インストールです。python -m pip install pyperclip を実行してください。") from exc

    pyperclip.copy(text)
    app = Application(backend="uia").start("notepad.exe")
    win = app.window(title_re=".*(Notepad|メモ帳).*", found_index=0)
    win.wait("visible", timeout=10)
    win.set_focus()
    win.type_keys("^v")

    title = win.window_text()
    log_file = append_action_log(
        tool="pywinauto",
        action="run_notepad_demo",
        status="success",
        detail={"window_title": title, "text_len": len(text)},
    )
    return WindowsRunResult(
        action="run_notepad_demo",
        status="success",
        window_title=title,
        detail="メモ帳を起動し、指定テキストを貼り付けました。保存はしていません。",
        log_file=str(log_file),
    )


def click_button_by_title(
    *,
    window_title_re: str,
    button_title: str,
    timeout: int = 10,
) -> WindowsRunResult:
    """Connect to a window and click a button by visible title.

    実業務アプリに使うための最小サンプル。
    更新・削除・確定・送信ボタンには使わないこと。
    """
    Desktop, _ = _import_pywinauto()
    desktop = Desktop(backend="uia")
    win = desktop.window(title_re=window_title_re)
    win.wait("visible", timeout=timeout)
    win.set_focus()
    btn = win.child_window(title=button_title, control_type="Button")
    btn.wait("enabled", timeout=timeout)
    btn.click_input()

    log_file = append_action_log(
        tool="pywinauto",
        action="click_button_by_title",
        status="success",
        detail={"window_title_re": window_title_re, "button_title": button_title},
    )
    return WindowsRunResult(
        action="click_button_by_title",
        status="success",
        window_title=win.window_text(),
        detail=f"ボタン {button_title} をクリックしました。",
        log_file=str(log_file),
    )
