from fastapi import APIRouter, Depends, HTTPException, Query, status

from recursiveops.api.deps import get_current_user, get_runner, get_settings
from recursiveops.core.parsing.journalctl import parse_journal_lines
from recursiveops.core.runner import CommandFailed, CommandNotAllowed

router = APIRouter(prefix="/logs", tags=["logs"])


def _run(runner, argv, use_sudo: bool = False):
    try:
        return runner.run(argv, check=True, use_sudo=use_sudo)
    except CommandNotAllowed as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except CommandFailed as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/systemd/{unit}")

def systemd_logs(
    unit: str,
    lines: int = Query(None, ge=1, le=2000),
    runner=Depends(get_runner),
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    tail_lines = lines or settings.checks.log_tail_lines
    result = _run(
        runner,
        ["journalctl", "-u", unit, "-n", str(tail_lines), "--no-pager", "-o", "short-iso"],
    )
    return parse_journal_lines(result.stdout)


@router.get("/journal")
def journal_logs(
    lines: int = Query(None, ge=1, le=5000),
    runner=Depends(get_runner),
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    tail_lines = lines or settings.checks.log_tail_lines
    result = _run(
        runner,
        ["journalctl", "-n", str(tail_lines), "--no-pager", "-o", "short-iso"],
    )
    return parse_journal_lines(result.stdout)


@router.get("/podman/{container}")

def podman_logs(
    container: str,
    lines: int = Query(None, ge=1, le=2000),
    runner=Depends(get_runner),
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    tail_lines = lines or settings.checks.log_tail_lines
    result = _run(runner, ["podman", "logs", "--tail", str(tail_lines), container])
    return parse_journal_lines(result.stdout)
