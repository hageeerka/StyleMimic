# Этот код взят из проекта [ollama-telegram-ai] (https://github.com/kirillzhosul/ollama-telegram-ai)
# Автор: Kirill Zhosul
# Лицензия: MIT

"""
API wrapper around ollama

TODO: Plain (non-chat) implementation
TODO: Full Async HTTP
"""

import time
from functools import lru_cache
from json import loads
from logging import getLogger
from typing import Union, Tuple, AsyncGenerator, Any, Final, Optional


import aiohttp
import aiohttp.client_exceptions

from bot.settings import OLLAMA_API_HOST, OLLAMA_KEEP_ALIVE

from .dto import (
    OllamaChatMessage,
    OllamaCompletionFinalChunk,
    OllamaCompletionResponseChunk,
    OllamaErrorChunk,
    OllamaModelTag,
)

logger = getLogger("ollama.api")


def get_ttl_hash(seconds: int = 3600) -> int:
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)


@lru_cache()
async def get_installed_models(*, cache_ttl: Optional[int] = None) -> list[OllamaModelTag]:
    del cache_ttl
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{OLLAMA_API_HOST}/api/tags") as response:
            return [
                OllamaModelTag.model_validate(tag)
                for tag in ((await response.json()).get("models", []))
            ]


async def model_is_installed(model_id: str) -> bool:
    for model in await get_installed_models(cache_ttl=get_ttl_hash):
        if model.name in (model_id, f"{model_id}:latest"):
            return True
    return False


async def ollama_is_healthy() -> bool:
    try:
        await get_installed_models()
    except aiohttp.client_exceptions.ClientError:
        return False
    return True


async def generate_raw_chat_completion(
    messages: list[OllamaChatMessage],
    model: str,
    **ollama_options: Any,
) -> AsyncGenerator[dict[str, Any], Any]:
    """
    Generates chunked chat response and returns it as-is (raw)
    """
    RESPONSE_SEGMENT_ENCODING: Final[str] = "utf-8"

    ollama_params: dict[str, Any] = {
        "model": model,
        "messages": [message.model_dump() for message in messages],
        "stream": True,
        "options": ollama_options,
        "keep_alive": OLLAMA_KEEP_ALIVE,
    }
    logger.debug(f"Requesting chat completion with {model=}...")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{OLLAMA_API_HOST}/api/chat", json=ollama_params
        ) as response:
            async for segment in response.content:
                if not segment:
                    continue

                raw_segment = segment.decode(RESPONSE_SEGMENT_ENCODING)
                if raw_segment.strip():
                    raw_segment = loads(raw_segment)
                    yield raw_segment


async def generate_chat_completion(
        system_prompt: str,
        messages: list[OllamaChatMessage],
        model: str,
        **ollama_options: Any,
) -> AsyncGenerator[Tuple[bool, Union[OllamaCompletionResponseChunk, OllamaErrorChunk]], None]:
    """
    Generates chunked chat response with a system prompt
    """
    messages.insert(0, OllamaChatMessage(role="system", content=system_prompt))

    async for raw_segment in generate_raw_chat_completion(
            messages, model, **ollama_options
    ):
        if "error" in raw_segment:
            yield False, OllamaErrorChunk(error=raw_segment["error"])
        segment_dto = OllamaCompletionResponseChunk
        if is_done := raw_segment.get("done", False):
            segment_dto = OllamaCompletionFinalChunk
        yield is_done, segment_dto.model_validate(raw_segment)


async def validate_installation_with_configuration(
    required_model_id: Optional[str] = None,
):
    if not await ollama_is_healthy():
        print("[FATAL] Ollama seems not be healthy, is it up and running?")
        exit(1)

    if required_model_id is None:
        return

    if not await model_is_installed(required_model_id):
        print(f"[FATAL] Model {required_model_id} is not installed")
        installed_models = await get_installed_models()
        if not installed_models:
            print(
                "[WARNING]: Seems like no models installed, you should install any model and configure bot to use it!"
            )
        exit(1)
