from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from recursiveops.api.deps import get_current_user, get_settings
from recursiveops.core.redact import redact_secrets
from recursiveops.llm import get_llm_client
from recursiveops.llm.base import LLMError
from recursiveops.llm.ollama import OllamaClient
from recursiveops.llm.schemas import FailureExplanation
from fastapi.responses import StreamingResponse
import httpx
import json

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
    generate_ok = False
    generate_error = None
    if model_ok:
        gen_url = f"{base_url}/api/generate"
        payload = {
            "model": settings.llm.ollama.model,
            "prompt": "ping",
            "stream": False,
            "options": {"num_predict": 1},
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                gen_response = await client.post(gen_url, json=payload)
                if gen_response.status_code >= 400:
                    detail = gen_response.text.strip()
                    generate_error = (
                        f"{gen_response.status_code} {gen_response.reason_phrase}"
                        + (f" - {detail}" if detail else "")
                    )
                else:
                    generate_ok = True
        except httpx.HTTPError as exc:
            generate_error = str(exc)
    return {
        "ok": model_ok and generate_ok,
        "base_url": base_url,
        "model": settings.llm.ollama.model,
        "models": models,
        "error": None if model_ok else "Model not found in Ollama tags",
        "generate_ok": generate_ok,
        "generate_error": generate_error,
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


@router.post("/explain-failure/stream")
async def explain_failure_stream(
    request: LLMRequest,
    _user=Depends(get_current_user),
    settings=Depends(get_settings),
):
    client = get_llm_client(settings)
    if not isinstance(client, OllamaClient):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Streaming only supported for Ollama")
    payload = _redact_payload(request.payload)
    prompt = client.build_failure_prompt(payload)
    base_url = client.base_url.rstrip("/")

    async def event_stream():
        raw_parts: list[str] = []
        url = f"{base_url}/api/generate"
        body = {"model": client.model, "prompt": prompt, "stream": True}
        try:
            async with httpx.AsyncClient(timeout=None) as http:
                async with http.stream("POST", url, json=body) as response:
                    if response.status_code >= 400:
                        detail = (await response.aread()).decode(errors="ignore").strip()
                        message = (
                            f"Ollama request failed: {response.status_code} {response.reason_phrase}"
                            + (f" - {detail}" if detail else "")
                        )
                        yield f"data: {json.dumps({'type': 'error', 'message': message})}\n\n"
                        return
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        chunk = data.get("response") or ""
                        if chunk:
                            raw_parts.append(chunk)
                            yield f"data: {json.dumps({'type': 'delta', 'text': chunk})}\n\n"
                        if data.get("done"):
                            break
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
            return

        raw = "".join(raw_parts).strip()
        try:
            parsed = json.loads(raw)
            FailureExplanation.parse_obj(parsed)
            yield f"data: {json.dumps({'type': 'result', 'data': parsed})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Invalid JSON response: {exc}'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


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
