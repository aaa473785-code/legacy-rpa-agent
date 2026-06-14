from __future__ import annotations

from pathlib import Path
import os

import pandas as pd
import streamlit as st

from llm_clients import MODEL_CATALOG, SYSTEM_PROMPT, call_llm, get_model_info
from tools.action_logger import read_action_log
from tools.browser_tools import dry_run_browser_action
from tools.csv_tools import read_csv_preview
from tools.playwright_tools import run_sample_customer_search
from tools.report_tools import save_markdown_report
from tools.windows_tools import list_top_windows, run_notepad_demo


st.set_page_config(
    page_title="業務操作AIエージェント",
    page_icon="🧰",
    layout="wide",
)


DEFAULT_TASK = """顧客検索アプリで「山田」を検索して、検索結果CSVを出力し、件数と注意点を報告する。"""


def render_sidebar():
    st.sidebar.markdown("## 🔑 APIキー")

    provider = st.sidebar.radio(
        "AIプロバイダー",
        list(MODEL_CATALOG.keys()),
        horizontal=True,
    )

    default_key = os.getenv("ANTHROPIC_API_KEY") if provider == "Anthropic" else os.getenv("OPENAI_API_KEY")
    if provider == "Anthropic":
        api_key = st.sidebar.text_input(
            "Anthropic API Key",
            type="password",
            value=default_key or "",
            placeholder="sk-ant-...",
        )
    else:
        api_key = st.sidebar.text_input(
            "OpenAI API Key",
            type="password",
            value=default_key or "",
            placeholder="sk-...",
        )

    st.sidebar.divider()
    st.sidebar.markdown("## ◎ モデル選択")

    labels = [model.label for model in MODEL_CATALOG[provider]]
    model_label = st.sidebar.selectbox("モデル", labels)
    model_info = get_model_info(provider, model_label)

    model_id = st.sidebar.text_input("モデルID", value=model_info.model_id)
    st.sidebar.caption(f"入力: `{model_info.input_price}`　出力: `{model_info.output_price}`")
    if model_info.note:
        st.sidebar.caption(model_info.note)

    st.sidebar.divider()
    st.sidebar.markdown("## ⚙️ 実行設定")
    engine = st.sidebar.selectbox("操作エンジン", ["DRY RUN", "Playwright", "pywinauto"])
    max_tokens = st.sidebar.slider("最大出力トークン", 500, 8000, 2000, 500)
    dry_run = st.sidebar.toggle("危険操作は承認必須", value=True)

    return provider, api_key, model_info, model_id, max_tokens, dry_run, engine


def load_default_procedure() -> str:
    path = Path("procedures/sample_task.md")
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def build_prompt(task: str, procedure: str, csv_note: str, dry_run: bool, engine: str) -> str:
    return f"""
# ユーザー依頼
{task}

# 操作エンジン
{engine}

# 安全設定
{'危険操作は必ず人間承認を求める。' if dry_run else '検証モード。ただし削除・送信・発注・確定は人間承認必須。'}

# 業務手順書
{procedure}

# 参考データ
{csv_note}

上記にもとづいて、業務操作AIエージェントの実行計画と作業報告案を作ってください。
""".strip()


def render_ai_plan_tab(provider, api_key, model_info, model_id, max_tokens, dry_run, engine):
    left, right = st.columns([1.15, 0.85])

    with left:
        st.subheader("作業依頼")
        task = st.text_area("何をやらせるか", value=DEFAULT_TASK, height=120)

        st.subheader("業務手順書")
        procedure = st.text_area("手順書・運用ルール", value=load_default_procedure(), height=280)

        c1, c2 = st.columns(2)
        with c1:
            plan_only = st.button("プロンプトだけ確認", use_container_width=True)
        with c2:
            run_ai = st.button("AIで実行計画を作る", type="primary", use_container_width=True)

    with right:
        st.subheader("現在の設定")
        st.info(
            f"プロバイダー: **{provider}**\n\n"
            f"モデル: **{model_info.label}**\n\n"
            f"モデルID: `{model_id}`\n\n"
            f"操作エンジン: **{engine}**"
        )

        st.subheader("サンプルCSV確認")
        csv_path = "sample_data/customers.csv"
        try:
            preview = read_csv_preview(csv_path)
            st.dataframe(preview, use_container_width=True)
            csv_note = f"{csv_path} を確認済み。行数サンプル: {len(preview)}行。列: {', '.join(preview.columns)}"
        except Exception as exc:
            st.warning(str(exc))
            csv_note = "CSV未確認。"

        st.subheader("DRY RUNログ")
        st.code(dry_run_browser_action("顧客検索 → CSV出力", "サンプル業務アプリ"), language="text")

    should_call_ai = plan_only or run_ai
    if should_call_ai:
        prompt = build_prompt(task, procedure, csv_note, dry_run, engine)

        if plan_only:
            st.subheader("生成前プロンプト確認")
            st.code(prompt, language="markdown")
            return

        if not api_key:
            st.error(f"{provider} API Key を入力してください。")
            st.stop()

        with st.spinner(f"{provider} / {model_id} で生成中..."):
            try:
                result = call_llm(
                    provider=provider,
                    api_key=api_key,
                    model_id=model_id,
                    user_prompt=prompt,
                    system_prompt=SYSTEM_PROMPT,
                    max_tokens=max_tokens,
                )
            except Exception as exc:
                st.exception(exc)
                st.stop()

        st.subheader("AI実行計画・報告案")
        st.markdown(result)

        report_path = save_markdown_report(result)
        st.success(f"レポートを保存しました: {report_path}")


def render_playwright_tab():
    st.subheader("🌐 Playwright Web操作")
    st.write("同梱のサンプルWeb画面を実際に開き、検索、CSV出力、スクリーンショット保存まで実行します。")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        keyword = st.text_input("検索キーワード", value="山田")
    with col2:
        headless = st.toggle("ヘッドレス実行", value=True)
    with col3:
        slow_mo_ms = st.number_input("slow_mo ms", min_value=0, max_value=2000, value=0, step=100)

    custom_url = st.text_input("対象URL（空なら同梱サンプル）", value="")

    if st.button("Playwrightサンプル実行", type="primary"):
        with st.spinner("Playwrightで画面操作中..."):
            try:
                result = run_sample_customer_search(
                    keyword=keyword,
                    headless=headless,
                    slow_mo_ms=int(slow_mo_ms),
                    url=custom_url.strip() or None,
                )
            except Exception as exc:
                st.exception(exc)
                st.stop()

        st.success("Playwright実行完了")
        st.json(result.to_dict())

        exported = Path(result.exported_csv)
        if exported.exists():
            st.subheader("出力CSV")
            st.dataframe(pd.read_csv(exported), use_container_width=True)

        screenshot = Path(result.screenshot)
        if screenshot.exists():
            st.subheader("スクリーンショット")
            st.image(str(screenshot), use_container_width=True)

    st.info("初回だけ `python -m playwright install chromium` が必要です。")


def render_pywinauto_tab():
    st.subheader("🪟 pywinauto Windows操作")
    st.write("Windowsネイティブアプリ操作の入口です。まずは安全なメモ帳デモと、開いているウィンドウ一覧の取得だけ入れています。")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("開いているウィンドウ一覧を取得"):
            try:
                infos = list_top_windows(limit=30)
            except Exception as exc:
                st.exception(exc)
                return
            st.dataframe([i.to_dict() for i in infos], use_container_width=True)

    with c2:
        text = st.text_area("メモ帳に貼り付けるテキスト", value="業務操作AIエージェント pywinauto demo\n保存・送信はしません。", height=120)
        if st.button("メモ帳デモ実行", type="primary"):
            try:
                result = run_notepad_demo(text=text)
            except Exception as exc:
                st.exception(exc)
                return
            st.success("pywinauto実行完了")
            st.json(result.to_dict())

    st.warning("pywinautoはWindows専用です。実業務アプリに接続する場合は、画面タイトルやボタン名を業務アプリに合わせて tools/windows_tools.py に追加してください。")


def render_logs_tab():
    st.subheader("📜 操作ログ")
    rows = read_action_log(limit=200)
    if not rows:
        st.info("まだ操作ログがありません。")
        return
    st.dataframe(rows, use_container_width=True)


def main():
    provider, api_key, model_info, model_id, max_tokens, dry_run, engine = render_sidebar()

    st.title("🧰 業務操作AIエージェント")
    st.caption("Anthropic / OpenAI切替 + Playwright / pywinauto操作PoC。旧RPA的な画面操作をAIで支援します。")

    tab1, tab2, tab3, tab4 = st.tabs(["AI計画", "Playwright実行", "pywinauto実行", "操作ログ"])
    with tab1:
        render_ai_plan_tab(provider, api_key, model_info, model_id, max_tokens, dry_run, engine)
    with tab2:
        render_playwright_tab()
    with tab3:
        render_pywinauto_tab()
    with tab4:
        render_logs_tab()


if __name__ == "__main__":
    main()
