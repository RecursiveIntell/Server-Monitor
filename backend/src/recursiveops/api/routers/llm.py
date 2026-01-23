from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from recursiveops.api.deps import get_current_user, get_settings
from recursiveops.core.redact import redact_secrets
from recursiveops.llm import get_llm_client
from recursiveops.llm.base import LLMError
import httpx

router = APIRouter(prefix="/llm", tags=["llm"])


class LLMRequest(BaseModel):
    payload: dict



def _redact_value(value):
    if isinstance(value, str):
        return redact_secrets(value)
    if isinstance(value, dict):
        return {key: _redact_value(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    return value


def _redact_payload(payload: dict) -> dict:
    return _redact_value(payload)


@router.get("/health")
async def llm_health(
    _user=Depends(get_current_user),
    settings=Depends(get_settings),
):
    if not settings.llm.enabled:
        return {"ok": False, "error": "LLM disabled", "base_url": settings.llm.ollama.base_url, "model": settings.llm.ollama.model}
    if settings.llm.provider != "ollama":
        return {"ok": False, "error": "LLM provider is not ollama", "provider": settings.llm.provider}
    base_url = settings.llm.ollama.base_url.rstrip("/")
    if base_url.endswith("/api"):
        base_url = base_url[: -len("/api")].rstrip("/")
    url = f"{base_url}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        return {
            "ok": False,
            "error": f"Ollama request failed: {exc}",
            "base_url": base_url,
            "model": settings.llm.ollama.model,
        }
    models = [m.get("name") for m in data.get("models", []) if isinstance(m, dict)]
    model_ok = settings.llm.ollama.model in models if settings.llm.ollama.model else False
    return {
        "ok": model_ok,
        "base_url": base_url,
        "model": settings.llm.ollama.model,
        "models": models,
        "error": None if model_ok else "Model not found in Ollama tags",
    }

@router.post("/explain-failure")
async def explain_failure(
    request: LLMRequest,
    _user=Depends(get_current_user),
    settings=Depends(get_settings),
):
    try:
        client = get_llm_client(settings)
        payload = _redact_payload(request.payload)
        result = await client.explain_failure(payload)
        return result.dict()
    except LLMError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/explain-diff")
async def explain_diff(
    request: LLMRequest,
    _user=Depends(get_current_user),
    settings=Depends(get_settings),
):
    try:
        client = get_llm_client(settings)
        payload = _redact_payload(request.payload)
        result = await client.explain_diff(payload)
        return result.dict()
    except LLMError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
