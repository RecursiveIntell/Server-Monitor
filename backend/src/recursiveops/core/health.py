from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed


@dataclass
class HealthCheckResult:
    ok: bool
    status_code: int | None
    response_time_ms: float | None
    error: str | None


@retry(stop=stop_after_attempt(2), wait=wait_fixed(0.5))
async def _fetch(url: str, timeout: float) -> httpx.Response:
    async with httpx.AsyncClient(timeout=timeout) as client:
        return await client.get(url)


async def check_url(url: str, timeout: float) -> HealthCheckResult:
    started = monotonic()
    try:
        response = await _fetch(url, timeout)
        elapsed = (monotonic() - started) * 1000
        ok = 200 <= response.status_code < 400
        return HealthCheckResult(ok=ok, status_code=response.status_code, response_time_ms=elapsed, error=None)
    except Exception as exc:  # pragma: no cover - defensive
        elapsed = (monotonic() - started) * 1000
        return HealthCheckResult(ok=False, status_code=None, response_time_ms=elapsed, error=str(exc))
