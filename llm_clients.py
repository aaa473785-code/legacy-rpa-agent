from __future__ import annotations

from typing import Any


SYSTEM_PROMPT = """あなたは業務操作AIエージェントです。
業務手順書を読み、RPA代替PoCとして安全な実行計画を作成します。

重要:
- ログイン情報の入力、データ更新、削除、確定、発注、本番書き込みは自動実行しない。
- 危険操作は必ず担当者による承認を挟む。
- APIやDBがある場合は、画面操作よりもAPI/DB利用を優先する。
- 画面操作する場合は、Playwrightまたはpywinautoのどちらを使うべきか明示する。
- 出力はMarkdownで、実行手順・確認事項・失敗時の切り戻しを含める。
"""


MODEL_CATALOG: dict[str, dict[str, Any]] = {
    "Anthropic": {
        "api_key_label": "Anthropic API Key",
        "api_key_placeholder": "sk-ant-...",
        "models": {
            "Haiku 4.5（高速・低コスト）": {
                "id": "claude-haiku-4-5",
                "input_price": "1.00/MTok",
                "output_price": "5.00/MTok",
            },
            "Sonnet 5（標準・高性能）": {
                "id": "claude-sonnet-5",
                "input_price": "3.00/MTok",
                "output_price": "15.00/MTok",
            },
        },
    },
    "OpenAI": {
        "api_key_label": "OpenAI API Key",
        "api_key_placeholder": "sk-...",
        "models": {
            "GPT-5.1（標準）": {
                "id": "gpt-5.1",
                "input_price": "モデル表を確認",
                "output_price": "モデル表を確認",
            },
            "GPT-5.1 mini（軽量）": {
                "id": "gpt-5.1-mini",
                "input_price": "モデル表を確認",
                "output_price": "モデル表を確認",
            },
        },
    },
}


def get_model_info(provider: str, model_label: str) -> dict[str, Any]:
    return MODEL_CATALOG[provider]["models"][model_label]


def call_llm(
    provider: str,
    api_key: str,
    model_id: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 2000,
) -> str:
    if provider == "Anthropic":
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        texts: list[str] = []
        for block in message.content:
            if getattr(block, "type", None) == "text":
                texts.append(block.text)
        return "\n".join(texts)

    if provider == "OpenAI":
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model_id,
            instructions=system_prompt,
            input=user_prompt,
            max_output_tokens=max_tokens,
        )
        return response.output_text

    raise ValueError(f"Unknown provider: {provider}")
