from __future__ import annotations

from enum import Enum


class LLMModels(str, Enum):
    GPT_OSS_20B = "accounts/fireworks/models/gpt-oss-20b"
    GPT_OSS_120B = "accounts/fireworks/models/gpt-oss-120b"

    DeepSeek_V4_Flash = "accounts/fireworks/models/deepseek-v4-flash"
    DeepSeek_V4_Pro = "accounts/fireworks/models/deepseek-v4-pro"

    Qwen_V37_PLUS = "accounts/fireworks/models/qwen3p7-plus"

    MINIMAX_M3 = "accounts/fireworks/models/minimax-m3"
