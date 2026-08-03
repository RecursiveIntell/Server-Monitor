from __future__ import annotations

import json
from pathlib import Path

import httpx
from pydantic import ValidationError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from recursiveops.llm.base import LLMClient, LLMError
from recursiveops.llm.schemas import DiffExplanation, FailureExplanation


class OllamaClient(LLMClient):
    def __init__(self, base_url: str, model: str):
        normalized = base_url.rstrip("/")
        if normalized.endswith("/api"):
            normalized = normalized[: -len("/api")].rstrip("/")
        self.base_url = normalized
        self.model = model

    def _load_prompt(self, name: str) -> str:
        prompt_path = Path(__file__).parent / "prompts" / name
        return prompt_path.read_text()

    def _render_prompt(self, name: str, payload: dict) -> str:
        template = self._load_prompt(name)
        if "{payload}" not in template:
            raise LLMError("LLM prompt missing payload placeholder")
        return template.replace("{payload}", json.dumps(payload))

    def build_failure_prompt(self, payload: dict) -> str:
        return self._render_prompt("explain_failure_v1.txt", payload)

    def build_diff_prompt(self, payload: dict) -> str:
        return self._render_prompt("explain_diff_v1.txt", payload)

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_fixed(1),
        reraise=True,
        retry=retry_if_exception_type(httpx.TransportError),
    )
    async def _generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            if response.status_code >= 400:
                detail = response.text.strip()
                raise LLMError(
                    f"Ollama request failed: {response.status_code} {response.reason_phrase}"
                    + (f" - {detail}" if detail else "")
                )
            data = response.json()
        return data.get("response", "")

    def _parse_json(self, raw: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LLMError("LLM response was not valid JSON") from exc

    async def explain_failure(self, payload: dict) -> FailureExplanation:
        prompt = self._render_prompt("explain_failure_v1.txt", payload)
        try:
            raw = await self._generate(prompt)
        except httpx.HTTPError as exc:
            raise LLMError(f"Ollama request failed: {exc}") from exc
        data = self._parse_json(raw)
        try:
            return FailureExplanation.parse_obj(data)
        except ValidationError as exc:
            raise LLMError("LLM response did not match schema") from exc

    async def explain_diff(self, payload: dict) -> DiffExplanation:
        prompt = self._render_prompt("explain_diff_v1.txt", payload)
        try:
            raw = await self._generate(prompt)
        except httpx.HTTPError as exc:
            raise LLMError(f"Ollama request failed: {exc}") from exc
        data = self._parse_json(raw)
        try:
            return DiffExplanation.parse_obj(data)
        except ValidationError as exc:
            raise LLMError("LLM response did not match schema") from exc
