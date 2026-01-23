from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from recursiveops.api.deps import get_current_user, get_session, get_settings
from recursiveops.auth.models import Token, User, UserLogin, UserRead
from recursiveops.auth.security import (
    create_access_token,
    get_jwt_secret,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(payload: UserLogin, session: Session = Depends(get_session), settings=Depends(get_settings)):
    statement = select(User).where(User.username == payload.username)
    user = session.exec(statement).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
    secret = get_jwt_secret(settings)
    token = create_access_token({"sub": user.username}, secret)
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return UserRead(
        id=current_user.id,
        username=current_user.username,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
    )
