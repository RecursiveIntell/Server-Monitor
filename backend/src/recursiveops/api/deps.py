from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from recursiveops.auth.models import User
from recursiveops.auth.security import TokenError, get_jwt_secret, safe_decode_token
from recursiveops.settings import Settings


security_scheme = HTTPBearer(auto_error=False)


async def get_settings(request: Request) -> Settings:
    return request.app.state.settings


async def get_engine_dep(request: Request):
    return request.app.state.engine


async def get_session(engine=Depends(get_engine_dep)):
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


async def get_runner(request: Request):
    return request.app.state.runner


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_session),
) -> User:
    if not settings.security.require_login:
        return None
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = credentials.credentials
    secret = get_jwt_secret(settings)
    try:
        payload = safe_decode_token(token, secret)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
    return user
