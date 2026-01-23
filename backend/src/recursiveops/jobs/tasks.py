from __future__ import annotations

import asyncio

from sqlmodel import Session, select

from recursiveops.core.health import check_url
from recursiveops.db.models import HealthCheck, HealthResult
from recursiveops.settings import Settings


def run_scheduled_checks(session: Session, settings: Settings) -> None:
    checks = session.exec(select(HealthCheck).where(HealthCheck.enabled == True)).all()
    if not checks:
        return

    async def _run() -> None:
        for check in checks:
            result = await check_url(check.url, settings.checks.http_timeout_seconds)
            session.add(
                HealthResult(
                    check_id=check.id,
                    ok=result.ok,
                    status_code=result.status_code,
                    response_time_ms=result.response_time_ms,
                    error=result.error,
                )
            )
        session.commit()

    asyncio.run(_run())
