from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from recursiveops.api.deps import get_current_user, get_session, get_settings
from recursiveops.core.patch import apply_yaml_patch, preview_unified_diff
from recursiveops.core.permissions import actions_allowed
from recursiveops.core.snapshot import create_snapshot, restore_snapshot
from recursiveops.db.models import ChangeRecord, Snapshot
from recursiveops.integrations.cloudflared import parse_cloudflared_yaml

router = APIRouter(prefix="/routes/cloudflared", tags=["routes"])


class CloudflaredPreview(BaseModel):
    new_config: str


class CloudflaredApply(CloudflaredPreview):
    reason: str | None = None


class CloudflaredRollback(BaseModel):
    snapshot_id: int


@router.get("")

def list_routes(settings=Depends(get_settings), _user=Depends(get_current_user)):
    path = Path(settings.paths.cloudflared_config)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cloudflared config not found")
    routes = parse_cloudflared_yaml(path.read_text())
    return [route.__dict__ for route in routes]


@router.post("/preview")

def preview_routes(request: CloudflaredPreview, settings=Depends(get_settings), _user=Depends(get_current_user)):
    path = Path(settings.paths.cloudflared_config)
    current = path.read_text() if path.exists() else ""
    diff = preview_unified_diff(current, request.new_config, str(path))
    return {"diff": diff}


@router.post("/apply")

def apply_routes(
    request: CloudflaredApply,
    settings=Depends(get_settings),
    session: Session = Depends(get_session),
    _user=Depends(get_current_user),
):
    if not actions_allowed(settings):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Actions disabled")
    path = Path(settings.paths.cloudflared_config)
    current = path.read_text() if path.exists() else ""
    snapshot = create_snapshot(session, str(path), current)
    diff = apply_yaml_patch(path, request.new_config)
    change = ChangeRecord(path=str(path), diff=diff, snapshot_id=snapshot.id)
    session.add(change)
    session.commit()
    session.refresh(change)
    return {"change_id": change.id, "diff": diff}


@router.post("/rollback")

def rollback_routes(
    request: CloudflaredRollback,
    session: Session = Depends(get_session),
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    if not actions_allowed(settings):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Actions disabled")
    snapshot = session.get(Snapshot, request.snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snapshot not found")
    restore_snapshot(Path(snapshot.path), snapshot)
    return {"status": "ok"}
