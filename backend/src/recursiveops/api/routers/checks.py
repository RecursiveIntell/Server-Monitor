from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from recursiveops.api.deps import get_current_user, get_session, get_settings
from recursiveops.core.health import check_url
from recursiveops.db.models import HealthCheck, HealthResult

router = APIRouter(prefix="/checks", tags=["checks"])


class HealthCheckCreate(BaseModel):
    name: str
    url: str
    interval_seconds: int | None = None


@router.get("")

def list_checks(session: Session = Depends(get_session), _user=Depends(get_current_user)):
    return session.exec(select(HealthCheck)).all()


@router.post("")

def create_check(
    payload: HealthCheckCreate,
    session: Session = Depends(get_session),
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    interval = payload.interval_seconds or settings.checks.default_interval_seconds
    check = HealthCheck(name=payload.name, url=payload.url, interval_seconds=interval, enabled=True)
    session.add(check)
    session.commit()
    session.refresh(check)
    return check


@router.get("/{check_id}/results")

def list_results(check_id: int, session: Session = Depends(get_session), _user=Depends(get_current_user)):
    return session.exec(
        select(HealthResult).where(HealthResult.check_id == check_id).order_by(HealthResult.checked_at.desc())
    ).all()


@router.post("/{check_id}/run")
async def run_check(
    check_id: int,
    session: Session = Depends(get_session),
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    check = session.get(HealthCheck, check_id)
    if not check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check not found")

    result = await check_url(check.url, settings.checks.http_timeout_seconds)
    record = HealthResult(
        check_id=check.id,
        ok=result.ok,
        status_code=result.status_code,
        response_time_ms=result.response_time_ms,
        error=result.error,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record
