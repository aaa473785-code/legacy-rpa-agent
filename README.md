# 業務操作AIエージェント

レガシー業務画面の操作手順を読み、AIが実行計画を作成し、Playwright / pywinauto / CSV確認 / Markdown報告に分解するRPA代替PoCです。

リポジトリ名やフォルダ名は `legacy-rpa-agent` のままで問題ありません。画面上のアプリ名は「業務操作AIエージェント」です。

## 主な機能

- Anthropic / OpenAI のモデル切り替え
- 業務手順書の読み込み
- AIによる実行計画作成
- PlaywrightによるWeb画面操作デモ
- pywinautoによるWindowsアプリ操作デモ
- CSVの件数・空欄・重複チェック
- 操作ログの記録

## 起動方法

```powershell
cd C:\PoC\legacy-rpa-agent
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m streamlit run app.py
```

## 重要な安全ルール

- ログイン情報の入力は担当者が行う。
- データ更新、削除、確定、発注、本番書き込みはAIが直接実行しない。
- 危険操作は担当者による承認を必須にする。
- `.env`、`logs`、`downloads` はGit管理しない。

## 手順書の場所

```text
procedures/sample_task.md
```

PADで作成した大まかな業務フローは、このファイルに貼り付けて使えます。  
ただし、パスワード、APIキー、本番URL、個人情報、社内サーバー名などは削除または伏せてから貼り付けてください。

## GitHubへ上げる前の確認

```powershell
git status
```

`.env`、`logs/`、`downloads/` が含まれていないことを確認してください。
