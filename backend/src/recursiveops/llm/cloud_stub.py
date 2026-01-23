from __future__ import annotations

from recursiveops.llm.base import LLMClient, LLMError
from recursiveops.llm.schemas import DiffExplanation, FailureExplanation


class CloudStubClient(LLMClient):
    async def explain_failure(self, payload: dict) -> FailureExplanation:
        raise LLMError("Cloud LLM provider not configured")

    async def explain_diff(self, payload: dict) -> DiffExplanation:
        raise LLMError("Cloud LLM provider not configured")
