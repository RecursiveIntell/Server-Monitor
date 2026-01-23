from __future__ import annotations

from recursiveops.llm.base import LLMClient, LLMError
from recursiveops.llm.cloud_stub import CloudStubClient
from recursiveops.llm.ollama import OllamaClient
from recursiveops.settings import Settings


def get_llm_client(settings: Settings) -> LLMClient:
    if not settings.llm.enabled:
        raise LLMError("LLM disabled")
    if settings.llm.provider == "ollama":
        return OllamaClient(settings.llm.ollama.base_url, settings.llm.ollama.model)
    if settings.llm.provider == "cloud" and settings.llm.cloud.enabled:
        return CloudStubClient()
    raise LLMError("LLM provider not configured")
