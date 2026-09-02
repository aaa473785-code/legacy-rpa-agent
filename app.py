from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from llm_clients import MODEL_CATALOG, SYSTEM_PROMPT, call_llm, get_model_info
from tools.action_logger import read_action_log
from tools.browser_tools import dry_run_browser_action
from tools.csv_tools import read_csv_preview
from tools.playwright_tools import run_sample_customer_search
from tools.report_tools import save_markdown_report
from tools.windows_tools import list_top_windows, run_notepad_demo


BASE_DIR = Path(__file__).resolve().parent
PROCEDURE_PATH = BASE_DIR / "procedures" / "sample_task.md"
SAMPLE_CSV_PATH = BASE_DIR / "sample_data" / "customers.csv"
LOG_PATH = BASE_DIR / "logs" / "actions.jsonl"


st.set_page_config(
    page_title="業務操作AIエージェント",
    page_icon="🤖",
    layout="wide",
)


DEFAULT_TASK = "顧客検索アプリで「山田」を検索して、検索結果CSVを出力し、件数と注意点を報告する。"


def read_text_utf8(path: Path, default: str = "") -> str:
    """UTF-8前提で読む。BOM付きUTF-8にも対応する。"""
    if not path.exists():
        return default

    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def render_sidebar():
    st.sidebar.markdown("## 🔑 APIキー")

    provider = st.sidebar.radio(
        "AIプロバイダー",
        list(MODEL_CATALOG.keys()),
        horizontal=True,
    )

    provider_conf = MODEL_CATALOG[provider]

    api_key = st.sidebar.text_input(
        provider_conf["api_key_label"],
        type="password",
        placeholder=provider_conf["api_key_placeholder"],
    )

    st.sidebar.divider()
    st.sidebar.markdown("## ◎ モデル選択")

    model_label = st.sidebar.selectbox(
        "モデル",
        list(provider_conf["models"].keys()),
    )

    model_info = get_model_info(provider, model_label)

    st.sidebar.caption(f"モデルID: `{model_info['id']}`")
    st.sidebar.caption(
        f"入力: `{model_info['input_price']}`　出力: `{model_info['output_price']}`"
    )

    st.sidebar.divider()
    st.sidebar.markdown("## ⚙️ 実行設定")
    dry_run = st.sidebar.checkbox("DRY RUN（安全実行）", value=True)
    require_approval = st.sidebar.checkbox("危険操作は担当者承認を必須にする", value=True)

    return provider, api_key, model_label, model_info["id"], dry_run, require_approval


def build_user_prompt(
    task_text: str,
    procedure_text: str,
    dry_run: bool,
    require_approval: bool,
) -> str:
    return f"""
以下の業務タスクと手順書を読み、RPA代替PoCとしての実行計画を作成してください。

# 業務タスク
{task_text}

# 業務手順書
{procedure_text}

# 制約
- DRY RUN: {dry_run}
- 危険操作の担当者承認: {require_approval}
- ログイン、更新、削除、確定、発注、本番書き込みは自動実行しない。
- Playwright / pywinauto / CSV確認 / Markdown報告に分けて、実行計画を作る。
- 最後に、担当者が確認すべき点を箇条書きにする。
""".strip()


def render_procedure_box(procedure_text: str) -> None:
    """手順書を大きなMarkdown見出しにせず、コンパクトに表示する。"""
    with st.expander("業務手順書（クリックで表示）", expanded=False):
        st.text_area(
            "手順書・運用ルール",
            value=procedure_text,
            height=220,
            disabled=True,
            label_visibility="collapsed",
        )


def main() -> None:
    provider, api_key, model_label, model_id, dry_run, require_approval = render_sidebar()

    st.title("業務操作AIエージェント")
    st.caption("業務手順を読み、操作計画・CSV確認・報告作成を支援するPoC")

    task_text = st.text_area("依頼内容", value=DEFAULT_TASK, height=90)

    procedure_text = read_text_utf8(PROCEDURE_PATH, "手順書が見つかりません。")
    render_procedure_box(procedure_text)

    tab_plan, tab_playwright, tab_windows, tab_csv, tab_log = st.tabs(
        ["AI計画", "Playwright実行", "pywinauto実行", "CSV確認", "操作ログ"]
    )

    with tab_plan:
        st.subheader("AIによる実行計画")
        st.write(f"選択中: **{provider} / {model_label}**")

        if st.button("実行計画を作成", type="primary"):
            if not api_key:
                st.warning(f"{provider} APIキーを入力してください。APIなしでも他の実行タブは試せます。")
            else:
                prompt = build_user_prompt(task_text, procedure_text, dry_run, require_approval)
                with st.spinner("AIが実行計画を作成しています..."):
                    try:
                        result = call_llm(
                            provider=provider,
                            api_key=api_key,
                            model_id=model_id,
                            system_prompt=SYSTEM_PROMPT,
                            user_prompt=prompt,
                            max_tokens=2000,
                        )
                        st.markdown(result)

                        out_path = save_markdown_report(
                            result,
                            BASE_DIR / "downloads" / "ai_plan.md",
                        )
                        st.success(f"報告案を保存しました: {out_path}")
                    except Exception as e:
                        st.error("AI呼び出しでエラーになりました。")
                        st.exception(e)

        st.info("APIキーを入れずに画面操作デモだけ試す場合は、Playwright実行 / pywinauto実行 タブを使ってください。")

    with tab_playwright:
        st.subheader("Playwright実行デモ")
        st.write("同梱のサンプルWeb画面を開き、顧客検索、CSV出力、スクリーンショット保存を行います。")

        keyword = st.text_input("検索キーワード", value="山田")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("DRY RUN表示"):
                result = dry_run_browser_action(keyword)
                st.json(result)

        with col2:
            if st.button("Playwrightサンプル実行"):
                with st.spinner("PlaywrightでサンプルWeb画面を操作しています..."):
                    try:
                        result = run_sample_customer_search(BASE_DIR, keyword)
                        st.success("Playwright実行が完了しました。")
                        st.json(result)
                    except Exception as e:
                        st.error("Playwright実行でエラーになりました。")
                        st.exception(e)

    with tab_windows:
        st.subheader("pywinauto実行デモ")
        st.write("Windowsアプリ操作のPoCです。Windows環境でのみ動きます。")

        if st.button("開いているウィンドウ一覧を取得"):
            try:
                windows = list_top_windows()
                st.dataframe(pd.DataFrame(windows), use_container_width=True)
            except Exception as e:
                st.error("ウィンドウ一覧取得でエラーになりました。")
                st.exception(e)

        demo_text = st.text_area(
            "メモ帳に貼るテキスト",
            value="業務操作AIエージェント pywinauto デモ",
            height=80,
        )

        if st.button("メモ帳デモを実行"):
            try:
                result = run_notepad_demo(demo_text)
                st.success("メモ帳デモを実行しました。")
                st.json(result)
            except Exception as e:
                st.error("pywinauto実行でエラーになりました。")
                st.exception(e)

    with tab_csv:
        st.subheader("CSV確認")
        st.write("出力CSVの件数・空欄・重複を確認するデモです。")

        uploaded = st.file_uploader("CSVをアップロード", type=["csv"])
        target_path = SAMPLE_CSV_PATH

        if uploaded is not None:
            target_path = BASE_DIR / "downloads" / uploaded.name
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(uploaded.getvalue())

        if st.button("CSVを確認"):
            try:
                result = read_csv_preview(target_path)
                st.json(result["summary"])
                st.dataframe(result["preview"], use_container_width=True)
            except Exception as e:
                st.error("CSV確認でエラーになりました。")
                st.exception(e)

    with tab_log:
        st.subheader("操作ログ")
        log_rows = read_action_log(LOG_PATH)
        if log_rows:
            st.dataframe(pd.DataFrame(log_rows), use_container_width=True)
        else:
            st.info("まだ操作ログはありません。")


if __name__ == "__main__":
    main()
