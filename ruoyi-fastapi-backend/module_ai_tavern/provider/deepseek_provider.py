import time
from typing import Any

from openai import AsyncOpenAI

from config.env import AiTavernConfig


class DeepSeekProvider:
    @classmethod
    def _client(cls) -> AsyncOpenAI:
        return AsyncOpenAI(api_key=AiTavernConfig.deepseek_api_key, base_url=AiTavernConfig.deepseek_base_url)

    @classmethod
    async def chat(cls, messages: list[dict[str, str]], user_id: str, request_type: str = 'chat') -> dict[str, Any]:
        started_at = time.time()
        thinking_type = 'enabled' if AiTavernConfig.deepseek_thinking_enabled else 'disabled'
        response = await cls._client().chat.completions.create(
            model=AiTavernConfig.deepseek_model,
            messages=messages,
            max_tokens=AiTavernConfig.deepseek_max_tokens,
            stream=False,
            extra_body={
                'thinking': {'type': thinking_type},
                'user_id': user_id,
            },
        )
        latency_ms = int((time.time() - started_at) * 1000)
        choice = response.choices[0]
        message = choice.message
        return {
            'content': message.content or '',
            'reasoning_content': getattr(message, 'reasoning_content', None),
            'usage': response.usage,
            'latency_ms': latency_ms,
            'model': response.model or AiTavernConfig.deepseek_model,
            'request_id': response.id,
            'request_type': request_type,
        }
