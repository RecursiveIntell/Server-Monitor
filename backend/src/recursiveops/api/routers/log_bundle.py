from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from recursiveops.api.deps import get_current_user, get_runner, get_settings
from recursiveops.core.log_bundle import format_log_bundle
from recursiveops.core.parsing.journalctl import parse_journal_lines
from recursiveops.core.redact import redact_secrets
from recursiveops.core.runner import CommandFailed, CommandNotAllowed

router = APIRouter(prefix="/logs/bundle", tags=["logs"])


class BundleRequest(BaseModel):
    systemd_units: list[str] = []
    podman_containers: list[str] = []
    include_system: bool = False
    limit: int | None = None


@router.post("")
async def build_bundle(
    request: BundleRequest,
    runner=Depends(get_runner),
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    limit = request.limit or settings.checks.log_tail_lines
    sections = {}

    def _run(argv, use_sudo: bool = False):
        try:
            return runner.run(argv, check=True, use_sudo=use_sudo)
        except CommandNotAllowed as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except CommandFailed as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    if request.include_system:
        result = _run(
            ["journalctl", "-n", str(limit), "--no-pager", "-o", "short-iso"],
        )
        sections["system:journal"] = [redact_secrets(line) for line in parse_journal_lines(result.stdout)]

    for unit in request.systemd_units:
        result = _run(
            ["journalctl", "-u", unit, "-n", str(limit), "--no-pager", "-o", "short-iso"],
        )
        sections[f"systemd:{unit}"] = [redact_secrets(line) for line in parse_journal_lines(result.stdout)]

    for container in request.podman_containers:
        result = _run(["podman", "logs", "--tail", str(limit), container])
        sections[f"podman:{container}"] = [redact_secrets(line) for line in parse_journal_lines(result.stdout)]

    bundle = format_log_bundle(sections, limit=limit)
    return {"bundle": bundle}
