from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlmodel import Session

from recursiveops.api.deps import get_session, get_settings
from recursiveops.auth.security import create_access_token, get_jwt_secret
from recursiveops.auth.setup import create_initial_admin, requires_setup

router = APIRouter(prefix="/setup", tags=["setup"])


class SetupCreate(BaseModel):
    username: str
    password: str


def _ensure_local(request: Request) -> None:
    host = request.client.host if request.client else ""
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Setup is local-only")


@router.get("/status")
async def setup_status(request: Request, session: Session = Depends(get_session)):
    _ensure_local(request)
    return {"requires_setup": requires_setup(session)}


@router.post("/create")
async def setup_create(
    request: Request,
    payload: SetupCreate,
    session: Session = Depends(get_session),
    settings=Depends(get_settings),
):
    _ensure_local(request)
    if not requires_setup(session):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Setup already completed")
    try:
        user = create_initial_admin(session, payload.username, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    token = create_access_token({"sub": user.username}, get_jwt_secret(settings))
    return {"access_token": token, "token_type": "bearer"}
