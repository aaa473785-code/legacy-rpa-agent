# 業務操作AIエージェント

Anthropic / OpenAI を切り替えられる、レガシー業務アプリ操作AIエージェントPoCです。

> 内部フォルダ名・リポジトリ名は `legacy-rpa-agent` のままでも問題ありません。画面上の表示名だけ日本語化しています。

今回の版では、前回のDRY RUNだけでなく、以下を追加しています。

- PlaywrightによるWeb画面操作
- pywinautoによるWindowsネイティブアプリ操作
- 操作ログ `logs/actions.jsonl`
- サンプルWeb画面 `sample_web/customers.html`
- CSV出力・スクリーンショット保存

## できること

### AI側

- Anthropic / OpenAI の切り替え
- APIキー入力欄の切り替え
- プロバイダーごとのモデル選択
- モデルIDの手動変更
- 業務手順書をもとにした作業計画生成

### Playwright側

- サンプル顧客検索ページを開く
- 顧客名を入力する
- 検索ボタンを押す
- CSV出力ボタンを押す
- `downloads/` にCSV保存
- `logs/` にスクリーンショット保存
- `logs/actions.jsonl` に操作ログ保存

### pywinauto側

- 開いているWindows画面一覧を取得
- メモ帳を起動してテキストを貼り付ける
- 実業務アプリ向けに、ウィンドウタイトル・ボタン名指定の操作関数を拡張可能

## 起動方法

```powershell
cd C:\Users\seesa\PoC\legacy-rpa-agent
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m streamlit run app.py
```

Playwrightは、pipでライブラリを入れた後にブラウザ本体も入れる必要があります。

## 画面構成

```text
🔑 APIキー

AIプロバイダー
[ Anthropic ] [ OpenAI ]

◎ モデル選択
Haiku / Sonnet / Opus
GPT-5.4 mini / GPT-5.4 / GPT-5.5

⚙️ 実行設定
操作エンジン: DRY RUN / Playwright / pywinauto
```

## 最初に試す順番

1. `python -m streamlit run app.py` で起動する。
2. 「Playwright実行」タブを開く。
3. 検索キーワードを `山田` にする。
4. 「Playwrightサンプル実行」を押す。
5. `downloads/` にCSV、`logs/` にスクリーンショットと操作ログが出ることを確認する。
6. Windowsなら「pywinauto実行」タブでメモ帳デモを試す。

## 実業務アプリに合わせる場所

Webアプリの場合は、ここを直します。

```text
tools/playwright_tools.py
```

具体的には、以下を実画面に合わせます。

```python
page.goto(url)
page.fill("#keyword", keyword)
page.click("#search")
page.click("#export")
```

Windowsアプリの場合は、ここを直します。

```text
tools/windows_tools.py
```

例えば、業務アプリの画面タイトルとボタン名に合わせます。

```python
click_button_by_title(
    window_title_re=".*業務アプリ.*",
    button_title="検索",
)
```

## 安全設計

このPoCでは、以下はAIに直接実行させない前提です。

- 削除
- 更新
- 送信
- 発注
- 確定
- 個人情報の外部送信

本番化する場合は、人間承認ID、操作者、対象案件ID、実行前後スクリーンショットをログに残してください。

## ファイル構成

```text
legacy-rpa-agent/  # 画面タイトル: 業務操作AIエージェント
├─ app.py
├─ llm_clients.py
├─ requirements.txt
├─ tools/
│  ├─ action_logger.py
│  ├─ browser_tools.py
│  ├─ playwright_tools.py
│  ├─ windows_tools.py
│  ├─ csv_tools.py
│  └─ report_tools.py
├─ procedures/
│  └─ sample_task.md
├─ sample_data/
│  └─ customers.csv
├─ sample_web/
│  └─ customers.html
├─ downloads/
├─ logs/
└─ scripts/
   └─ install_playwright.ps1
```
