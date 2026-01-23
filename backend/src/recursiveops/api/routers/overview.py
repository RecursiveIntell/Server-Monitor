from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from recursiveops.api.deps import get_current_user, get_runner
from recursiveops.core.parsing import parse_podman_ps, parse_systemctl_list
from recursiveops.core.runner import CommandFailed, CommandNotAllowed

router = APIRouter(prefix="/overview", tags=["overview"])


def _run_checked(runner, argv):
    try:
        return runner.run(argv, check=True)
    except CommandNotAllowed as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except CommandFailed as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("")
async def overview(runner=Depends(get_runner), _user=Depends(get_current_user)):
    systemd_result = _run_checked(
        runner,
        ["systemctl", "list-units", "--type=service", "--all", "--no-legend", "--no-pager"],
    )
    services = parse_systemctl_list(systemd_result.stdout)
    podman_result = _run_checked(runner, ["podman", "ps", "--all", "--format", "json"])
    containers = parse_podman_ps(podman_result.stdout)

    summary = {
        "services_total": len(services),
        "services_active": len([s for s in services if s.get("active") == "active"]),
        "services_failed": len([s for s in services if s.get("active") == "failed"]),
        "containers_total": len(containers),
        "containers_running": len([c for c in containers if c.get("State") == "running"]),
        "containers_exited": len([c for c in containers if c.get("State") == "exited"]),
    }
    return {"summary": summary, "services": services, "containers": containers}
