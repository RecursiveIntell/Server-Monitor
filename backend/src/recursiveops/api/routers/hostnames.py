from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

from recursiveops.api.deps import get_current_user, get_settings
from recursiveops.integrations.cloudflared import parse_cloudflared_yaml

router = APIRouter(prefix="/hostnames", tags=["hostnames"])


@router.get("")

def list_hostnames(settings=Depends(get_settings), _user=Depends(get_current_user)):
    path = Path(settings.paths.cloudflared_config)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cloudflared config not found")
    routes = parse_cloudflared_yaml(path.read_text())
    return [
        {"hostname": route.hostname, "service": route.service}
        for route in routes
        if route.hostname
    ]
