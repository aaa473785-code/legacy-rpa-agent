# 業務操作AIエージェント

PA（RPA）で30フロー作った実務経験をもとに、RPAでは対応しにくい「判断を伴う操作」をAIエージェントで補助するPoCです。

Playwright（Web画面操作）＋ pywinauto（Windowsアプリ操作）の2エンジン構成。  
削除・送信・発注・確定などの危険操作はAIが直接実行しない安全設計にしています。

## ファイル構成

```text
legacy-rpa-agent/
├── app.py                    # Streamlit本体
├── llm_clients.py            # Anthropic / OpenAI のモデル切り替え
├── requirements.txt          # パッケージ一覧
├── README.md
├── procedures/
│   └── sample_task.md        # 業務手順書サンプル
├── tools/
│   ├── playwright_tools.py   # Web画面操作
│   ├── windows_tools.py      # Windowsアプリ操作
│   ├── csv_tools.py          # CSV確認
│   ├── report_tools.py       # Markdown報告
│   ├── browser_tools.py      # DRY RUN用
│   └── action_logger.py      # 操作ログ
├── sample_web/
│   └── customers.html        # Playwright操作確認用サンプル画面
├── sample_data/
│   └── customers.csv         # CSV確認用サンプルデータ
├── logs/                     # 操作ログ出力先（Git管理外）
└── downloads/                # CSV・報告書出力先（Git管理外）
```

## セットアップ

```powershell
git clone https://github.com/aaa473785-code/legacy-rpa-agent.git
cd legacy-rpa-agent

python -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
python -m playwright install chromium
```

※ `venv/` はローカル環境用です。GitHubには含めません。  
※ pywinautoのデモはWindows環境でのみ動作します。

## 起動

```powershell
python -m streamlit run app.py
```

ブラウザで「業務操作AIエージェント」が開きます。

## ① AI計画

業務手順書と依頼内容を読み、AIが実行計画を作成します。

- Anthropic / OpenAI のプロバイダー切り替え
- モデル選択
- DRY RUN設定
- 危険操作の担当者承認設定
- Markdown形式の実行計画生成

対応モデルは `llm_clients.py` の `MODEL_CATALOG` で管理しています。

```text
Anthropic:
- Claude Haiku
- Claude Sonnet

OpenAI:
- GPT 標準モデル
- GPT 軽量モデル
```

モデルIDや価格は変わる可能性があるため、実運用時は各社の最新モデル表に合わせて `MODEL_CATALOG` を更新してください。

## ② Playwright実行

同梱のサンプルWeb画面を使って、Webアプリ操作の流れを確認できます。

- サンプルWeb画面を開く
- 顧客名を入力する
- 検索ボタンを押す
- スクリーンショットを保存する
- CSVを出力する

本番サイトを操作する前に、サンプル画面で動作確認するためのタブです。

## ③ pywinauto実行

Windowsネイティブアプリ操作のPoCです。

- 開いているウィンドウ一覧の取得
- メモ帳起動デモ
- テキスト入力デモ

実業務アプリへ適用する場合は、対象画面の要素名・ウィンドウ名・ボタン名を確認してから拡張します。

## ④ CSV確認

出力CSVの内容を確認します。

- 件数
- 列名
- 空欄セル数
- 重複行数
- プレビュー表示

RPAが出力したCSVを、AIエージェント側で後続確認する想定です。

## ⑤ 操作ログ

Playwright実行などの操作結果をログとして確認できます。

`logs/` 配下は実行時に生成されるため、GitHubには上げません。

## 業務手順書

手順書は以下に置きます。

```text
procedures/sample_task.md
```

PADで作成した大まかな業務フローは、このファイルに貼り付けて使えます。  
ただし、パスワード、APIキー、本番URL、個人情報、社内サーバー名などは削除または伏せてから貼り付けます。

## 安全設計

以下の操作はAIが直接実行しない前提です。

- ログイン情報の入力
- 個人情報を含むCSVの外部送信
- データ更新
- 削除
- 確定
- 発注
- 本番システムへの書き込み

危険操作は、担当者による承認を挟む設計にしています。

## GitHubへ上げる前の確認

```powershell
git status
```

以下がGit管理に含まれていないことを確認します。

```text
.env
venv/
logs/
downloads/
__pycache__/
```

※ PoCデモです。データはダミーです。
