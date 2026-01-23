from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from recursiveops.api.deps import get_current_user, get_runner
from recursiveops.core.parsing import (
    parse_findmnt,
    parse_firewall,
    parse_podman_ps,
    parse_ss,
    parse_systemctl_list,
)
from recursiveops.core.runner import CommandFailed, CommandNotAllowed

router = APIRouter(prefix="/inventory", tags=["inventory"])


def _run_or_409(runner, argv):
    try:
        return runner.run(argv, check=True)
    except CommandNotAllowed as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except CommandFailed as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/systemd")

def list_systemd(runner=Depends(get_runner), _user=Depends(get_current_user)):
    result = _run_or_409(
        runner, ["systemctl", "list-units", "--type=service", "--all", "--no-legend", "--no-pager"]
    )
    return parse_systemctl_list(result.stdout)


@router.get("/podman")

def list_podman(runner=Depends(get_runner), _user=Depends(get_current_user)):
    result = _run_or_409(runner, ["podman", "ps", "--all", "--format", "json"])
    return parse_podman_ps(result.stdout)


@router.get("/mounts")

def list_mounts(runner=Depends(get_runner), _user=Depends(get_current_user)):
    result = _run_or_409(runner, ["findmnt", "--json"])
    return parse_findmnt(result.stdout)


@router.get("/ports")

def list_ports(runner=Depends(get_runner), _user=Depends(get_current_user)):
    result = _run_or_409(runner, ["ss", "-tulpen"])
    return parse_ss(result.stdout)


@router.get("/firewall")

def firewall_status(runner=Depends(get_runner), _user=Depends(get_current_user)):
    result = _run_or_409(runner, ["firewall-cmd", "--list-all"])
    return parse_firewall(result.stdout)


@router.get("/summary")

def inventory_summary(runner=Depends(get_runner), _user=Depends(get_current_user)):
    summary = {
        "systemd": len(list_systemd(runner, _user)),
        "podman": len(list_podman(runner, _user)),
    }
    return summary
