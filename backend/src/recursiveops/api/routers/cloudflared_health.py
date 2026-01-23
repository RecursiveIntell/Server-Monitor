from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from recursiveops.api.deps import get_current_user, get_session, get_settings
from recursiveops.core.health import check_url
from recursiveops.db.models import HealthCheck, HealthResult
from recursiveops.integrations.cloudflared import build_health_targets, parse_cloudflared_yaml

router = APIRouter(prefix="/cloudflared", tags=["cloudflared"])


class HealthRunResponse(BaseModel):
    hostname: str
    url: str
    ok: bool
    status_code: int | None
    response_time_ms: float | None
    error: str | None


@router.get("/targets")
async def list_targets(
    settings=Depends(get_settings),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    path = Path(settings.paths.cloudflared_config)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cloudflared config not found")
    routes = parse_cloudflared_yaml(path.read_text())
    targets = build_health_targets(routes)
    for target in targets:
        check = session.exec(select(HealthCheck).where(HealthCheck.name == target["hostname"])).first()
        if not check:
            continue
        latest = session.exec(
            select(HealthResult)
            .where(HealthResult.check_id == check.id)
            .order_by(HealthResult.checked_at.desc())
        ).first()
        if latest:
            target["last_result"] = {
                "ok": latest.ok,
                "status_code": latest.status_code,
                "response_time_ms": latest.response_time_ms,
                "error": latest.error,
                "checked_at": latest.checked_at.isoformat(),
            }
    return targets


@router.post("/run")
async def run_targets(
    settings=Depends(get_settings),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    path = Path(settings.paths.cloudflared_config)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cloudflared config not found")
    routes = parse_cloudflared_yaml(path.read_text())
    targets = build_health_targets(routes)
    results: list[HealthRunResponse] = []

    for target in targets:
        result = await check_url(target["url"], settings.checks.http_timeout_seconds)
        results.append(
            HealthRunResponse(
                hostname=target["hostname"],
                url=target["url"],
                ok=result.ok,
                status_code=result.status_code,
                response_time_ms=result.response_time_ms,
                error=result.error,
            )
        )

        check = session.exec(select(HealthCheck).where(HealthCheck.name == target["hostname"])).first()
        if not check:
            check = HealthCheck(
                name=target["hostname"],
                url=target["url"],
                interval_seconds=settings.checks.default_interval_seconds,
                enabled=True,
            )
            session.add(check)
            session.commit()
            session.refresh(check)
        elif check.url != target["url"]:
            check.url = target["url"]
            session.add(check)
            session.commit()

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

    return {"results": [r.dict() for r in results]}
