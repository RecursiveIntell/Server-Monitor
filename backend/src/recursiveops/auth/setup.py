from __future__ import annotations

from sqlmodel import Session, select

from recursiveops.auth.models import User
from recursiveops.auth.security import hash_password


def requires_setup(session: Session) -> bool:
    return session.exec(select(User).limit(1)).first() is None


def create_initial_admin(session: Session, username: str, password: str) -> User:
    if not username or not password:
        raise ValueError("Username and password are required")
    if not requires_setup(session):
        raise ValueError("Setup already completed")
    existing = session.exec(select(User).where(User.username == username)).first()
    if existing:
        raise ValueError("User already exists")
    user = User(
        username=username,
        hashed_password=hash_password(password),
        is_active=True,
        is_admin=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
