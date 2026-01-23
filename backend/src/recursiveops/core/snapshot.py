from __future__ import annotations

from pathlib import Path

from sqlmodel import Session

from recursiveops.core.patch import atomic_write
from recursiveops.db.models import Snapshot


def create_snapshot(session: Session, path: str, content: str) -> Snapshot:
    snapshot = Snapshot(path=path, content=content)
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    return snapshot


def restore_snapshot(path: Path, snapshot: Snapshot) -> None:
    atomic_write(path, snapshot.content)
