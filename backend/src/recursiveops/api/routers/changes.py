from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from recursiveops.api.deps import get_current_user, get_session, get_settings
from recursiveops.core.permissions import actions_allowed
from recursiveops.core.snapshot import restore_snapshot
from recursiveops.db.models import ChangeRecord, Snapshot

router = APIRouter(prefix="/changes", tags=["changes"])


@router.get("")

def list_changes(session: Session = Depends(get_session), _user=Depends(get_current_user)):
    return session.exec(select(ChangeRecord).order_by(ChangeRecord.created_at.desc())).all()


@router.get("/{change_id}")

def get_change(change_id: int, session: Session = Depends(get_session), _user=Depends(get_current_user)):
    change = session.get(ChangeRecord, change_id)
    if not change:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Change not found")
    return change


@router.post("/{change_id}/rollback")

def rollback_change(
    change_id: int,
    session: Session = Depends(get_session),
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    if not actions_allowed(settings):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Actions disabled")
    change = session.get(ChangeRecord, change_id)
    if not change or not change.snapshot_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snapshot not found")
    snapshot = session.get(Snapshot, change.snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snapshot not found")
    restore_snapshot(Path(snapshot.path), snapshot)
    return {"status": "ok"}
