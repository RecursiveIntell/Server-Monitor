from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from recursiveops.api.deps import get_current_user, get_runner, get_settings
from recursiveops.core.permissions import actions_allowed
from recursiveops.core.runner import CommandFailed, CommandNotAllowed

router = APIRouter(prefix="/actions", tags=["actions"])


class SystemdAction(BaseModel):
    unit: str


def _ensure_allowed(settings):
    if not actions_allowed(settings):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Actions disabled")


def _run(runner, argv):
    try:
        return runner.run(argv, check=True)
    except CommandNotAllowed as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except CommandFailed as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/systemd/restart")

def restart_systemd(
    payload: SystemdAction,
    runner=Depends(get_runner),
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    _ensure_allowed(settings)
    result = _run(runner, ["systemctl", "restart", payload.unit])
    return {"status": "ok", "stderr": result.stderr.strip()}


@router.post("/systemd/reload")

def reload_systemd(
    payload: SystemdAction,
    runner=Depends(get_runner),
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    _ensure_allowed(settings)
    result = _run(runner, ["systemctl", "reload", payload.unit])
    return {"status": "ok", "stderr": result.stderr.strip()}
