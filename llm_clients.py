from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ModelInfo:
    label: str
    model_id: str
    input_price: str
    output_price: str
    note: str = ""


MODEL_CATALOG: Dict[str, List[ModelInfo]] = {
    "Anthropic": [
        ModelInfo(
            label="Haiku 4.5（高速・低コスト）",
            model_id="claude-haiku-4-5-20251001",
            input_price="$1.00/MTok",
            output_price="$5.00/MTok",
            note="軽い分類・短い指示・低コスト確認向け",
        ),
        ModelInfo(
            label="Sonnet 4.6（標準・高性能）",
            model_id="claude-sonnet-4-6",
            input_price="$3.00/MTok",
            output_price="$15.00/MTok",
            note="通常の業務エージェント向け",
        ),
        ModelInfo(
            label="Opus 4.8（高性能）",
            model_id="claude-opus-4-8",
            input_price="$5.00/MTok",
            output_price="$25.00/MTok",
            note="複雑な判断・長い手順書の理解向け",
        ),
    ],
    "OpenAI": [
        ModelInfo(
            label="GPT-5.4 mini（高速・低コスト）",
            model_id="gpt-5.4-mini",
            input_price="$0.75/MTok",
            output_price="$4.50/MTok",
            note="軽いエージェント処理向け",
        ),
        ModelInfo(
            label="GPT-5.4（標準・高性能）",
            model_id="gpt-5.4",
            input_price="$2.50/MTok",
            output_price="$15.00/MTok",
            note="標準モデル。業務手順の判断向け",
        ),
        ModelInfo(
            label="GPT-5.5（高性能）",
            model_id="gpt-5.5",
            input_price="$5.00/MTok",
            output_price="$30.00/MTok",
            note="複雑な推論・コード・業務判断向け",
        ),
    ],
}


SYSTEM_PROMPT = """あなたは legacy-rpa-agent の司令塔です。
目的は、レガシー業務アプリの作業手順を読み、実行計画を作り、操作ログとレポートを残すことです。
外部操作は Playwright / pywinauto などの専用ツールを通じて実行します。
削除、送信、発注、確定、個人情報の外部送信は必ず人間承認を要求してください。

以下を日本語で出力してください。
1. 作業目的
2. 前提確認
3. 操作ステップ
4. 使用する操作ツール候補（DRY RUN / Playwright / pywinauto）
5. 取得すべきCSV/DB/画面情報
6. 人間承認が必要な箇所
7. 失敗時の切り戻し
8. 最終レポート案
"""


def get_model_info(provider: str, label: str) -> ModelInfo:
    for model in MODEL_CATALOG[provider]:
        if model.label == label:
            return model
    raise KeyError(f"Unknown model label: {provider} / {label}")


def call_llm(
    *,
    provider: str,
    api_key: str,
    model_id: str,
    user_prompt: str,
    system_prompt: str = SYSTEM_PROMPT,
    max_tokens: int = 2000,
) -> str:
    """Call OpenAI or Anthropic with one shared interface."""
    provider = provider.strip()

    if provider == "Anthropic":
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError("anthropic が未インストールです。python -m pip install anthropic を実行してください。") from exc

        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "\n".join(
            block.text for block in message.content if getattr(block, "type", None) == "text"
        )

    if provider == "OpenAI":
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("openai が未インストールです。python -m pip install openai を実行してください。") from exc

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model_id,
            instructions=system_prompt,
            input=user_prompt,
            max_output_tokens=max_tokens,
        )
        return response.output_text

    raise ValueError(f"Unknown provider: {provider}")
