from openai import AsyncOpenAI
from app.config import settings
from app.schemas.LLMmodels import LLMModels

async def get_openai_client(api_key: str = settings.FireworksAPIKey) -> AsyncOpenAI:
    return AsyncOpenAI(api_key=api_key, base_url="https://api.fireworks.ai/inference/v1")

async def call_llm(prompt: str, system_prompt: str = None, model: LLMModels = LLMModels.GPT_OSS_20B, max_tokens: int = 2000, api_key: str = settings.FireworksAPIKey) -> str:
    client = await get_openai_client(api_key)
    messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    extra_body = {}
    if "gpt-oss" in model.value:
        # gpt-oss models emit a verbose internal "analysis" reasoning channel before
        # their final answer; keeping it short reduces the chance of running out of
        # max_tokens before the final-channel message is produced.
        extra_body["reasoning_effort"] = "low"

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        extra_body=extra_body or None,
    )
    content = response.choices[0].message.content
    if not content:
        finish_reason = response.choices[0].finish_reason
        raise RuntimeError(
            f"LLM ({model.value}) returned no content (finish_reason={finish_reason}). "
            "It likely ran out of tokens while reasoning — try increasing max_tokens."
        )
    return content

async def stream_llm(prompt: str, system_prompt: str = None, model: LLMModels = LLMModels.GPT_OSS_20B, max_tokens: int = 2000, api_key: str = settings.FireworksAPIKey):
    client = await get_openai_client(api_key)
    messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    stream = await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content