from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

from recursiveops.settings import Settings

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def load_jwt_secret(path: str | Path) -> str:
    secret_path = Path(path)
    return secret_path.read_text().strip()


def get_jwt_secret(settings: Settings) -> str:
    return load_jwt_secret(settings.security.jwt_secret_file)


def create_access_token(data: Dict[str, Any], secret: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret, algorithm=JWT_ALGORITHM)


def decode_token(token: str, secret: str) -> Dict[str, Any]:
    return jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])


class TokenError(Exception):
    pass


def safe_decode_token(token: str, secret: str) -> Dict[str, Any]:
    try:
        return decode_token(token, secret)
    except JWTError as exc:
        raise TokenError("Invalid token") from exc
