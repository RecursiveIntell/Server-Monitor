from __future__ import annotations

from abc import ABC, abstractmethod

from recursiveops.llm.schemas import DiffExplanation, FailureExplanation


class LLMError(Exception):
    pass


class LLMClient(ABC):
    @abstractmethod
    async def explain_failure(self, payload: dict) -> FailureExplanation:
        raise NotImplementedError

    @abstractmethod
    async def explain_diff(self, payload: dict) -> DiffExplanation:
        raise NotImplementedError
