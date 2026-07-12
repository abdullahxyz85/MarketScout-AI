from __future__ import annotations

from enum import Enum
from typing import AsyncIterator, Optional

from openai import AsyncOpenAI

from config import settings

FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1"


class FireworksModel(str, Enum):
    GPT_OSS_20B = "accounts/fireworks/models/gpt-oss-20b"
    GPT_OSS_120B = "accounts/fireworks/models/gpt-oss-120b"
    DEEPSEEK_V4_FLASH = "accounts/fireworks/models/deepseek-v4-flash"
    DEEPSEEK_V4_PRO = "accounts/fireworks/models/deepseek-v4-pro"
    QWEN_V37_PLUS = "accounts/fireworks/models/qwen3p7-plus"
    MINIMAX_M3 = "accounts/fireworks/models/minimax-m3"


def _get_client(api_key: Optional[str] = None) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=api_key or settings.FIREWORKS_API_KEY,
        base_url=FIREWORKS_BASE_URL,
    )


async def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: FireworksModel = FireworksModel.DEEPSEEK_V4_FLASH,
    max_tokens: int = 2000,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None,
) -> str:
    """Call the Fireworks AI LLM (AMD Instinct GPU-backed) and return the full response.

    Pass temperature=0 for deterministic scoring agents; omit for creative/narrative agents.
    """
    client = _get_client(api_key)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    create_kwargs: dict = dict(model=model, messages=messages, max_tokens=max_tokens)
    if temperature is not None:
        create_kwargs["temperature"] = temperature
    response = await client.chat.completions.create(**create_kwargs)
    return response.choices[0].message.content


async def stream_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: FireworksModel = FireworksModel.DEEPSEEK_V4_FLASH,
    max_tokens: int = 2000,
    api_key: Optional[str] = None,
) -> AsyncIterator[str]:
    """Stream tokens from the Fireworks AI LLM as they are generated."""
    client = _get_client(api_key)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
