from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
import yaml
from sqlmodel import Session

from recursiveops.api.deps import get_current_user, get_session, get_settings
from recursiveops.core.patch import apply_yaml_patch, preview_unified_diff
from recursiveops.core.permissions import actions_allowed
from recursiveops.core.snapshot import create_snapshot
from recursiveops.db.models import ChangeRecord
from recursiveops.settings import public_settings
from recursiveops.settings import load_settings, set_settings_cache
from recursiveops.settings_update import apply_llm_update

router = APIRouter(prefix="/settings/llm", tags=["settings"])


class LLMUpdate(BaseModel):
    enabled: bool | None = None
    provider: str | None = None
    ollama: dict | None = None
    cloud: dict | None = None


def _build_updated_config(settings, payload: dict) -> tuple[Path, str, str]:
    if not settings.config_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Config path not set")
    config_path = Path(settings.config_path)
    current_text = config_path.read_text() if config_path.exists() else ""
    data = yaml.safe_load(current_text) or {}
    updated = apply_llm_update(data, payload)
    new_text = yaml.safe_dump(updated, sort_keys=False)
    return config_path, current_text, new_text


@router.post("/preview")
async def preview_llm_settings(
    request: LLMUpdate,
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    config_path, current_text, new_text = _build_updated_config(
        settings, request.dict(exclude_none=True)
    )
    diff = preview_unified_diff(current_text, new_text, str(config_path))
    return {"diff": diff}


@router.post("/apply")
async def apply_llm_settings(
    request: LLMUpdate,
    request_ctx: Request,
    session: Session = Depends(get_session),
    settings=Depends(get_settings),
    _user=Depends(get_current_user),
):
    if not actions_allowed(settings):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Actions disabled")
    config_path, current_text, new_text = _build_updated_config(
        settings, request.dict(exclude_none=True)
    )
    snapshot = create_snapshot(session, str(config_path), current_text)
    diff = apply_yaml_patch(config_path, new_text)
    change = ChangeRecord(path=str(config_path), diff=diff, snapshot_id=snapshot.id)
    session.add(change)
    session.commit()
    session.refresh(change)

    new_settings = load_settings(config_path)
    request_ctx.app.state.settings = new_settings
    set_settings_cache(new_settings)
    return {"change_id": change.id, "diff": diff, "settings": public_settings(new_settings)}
