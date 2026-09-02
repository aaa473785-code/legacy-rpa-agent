from __future__ import annotations

from datetime import datetime


def list_top_windows() -> list[dict]:
    try:
        from pywinauto import Desktop
    except ImportError as exc:
        raise RuntimeError("pywinauto が入っていません。`python -m pip install -r requirements.txt` を実行してください。") from exc

    windows = []
    for w in Desktop(backend="uia").windows():
        try:
            title = w.window_text()
            if title:
                windows.append(
                    {
                        "title": title,
                        "class_name": w.class_name(),
                        "control_id": getattr(w, "control_id", lambda: "")(),
                    }
                )
        except Exception:
            continue
    return windows


def run_notepad_demo(text: str) -> dict:
    try:
        from pywinauto.application import Application
    except ImportError as exc:
        raise RuntimeError("pywinauto が入っていません。`python -m pip install -r requirements.txt` を実行してください。") from exc

    app = Application(backend="uia").start("notepad.exe")
    dlg = app.window(title_re=".*メモ帳.*|.*Notepad.*")
    dlg.wait("visible", timeout=10)
    dlg.type_keys(text, with_spaces=True, set_foreground=True)

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "action": "notepad_demo",
        "text": text,
    }
