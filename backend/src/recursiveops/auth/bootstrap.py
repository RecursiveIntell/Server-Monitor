from __future__ import annotations

import argparse

from sqlmodel import Session, select

from recursiveops.auth.models import User
from recursiveops.auth.security import hash_password
from recursiveops.db.engine import get_engine
from recursiveops.settings import get_settings


def ensure_admin(username: str, password: str) -> bool:
    settings = get_settings()
    engine = get_engine(settings)
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.username == username)).first()
        if existing:
            return False
        user = User(
            username=username,
            hashed_password=hash_password(password),
            is_active=True,
            is_admin=True,
        )
        session.add(user)
        session.commit()
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or ensure an admin user.")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    created = ensure_admin(args.username, args.password)
    if created:
        print("Admin user created")
    else:
        print("Admin user already exists")


if __name__ == "__main__":
    main()
