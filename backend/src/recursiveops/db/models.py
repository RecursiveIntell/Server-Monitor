from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ChangeRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    path: str
    diff: str
    status: str = "applied"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    snapshot_id: Optional[int] = Field(default=None, foreign_key="snapshot.id")


class Snapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    path: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HealthCheck(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    url: str
    interval_seconds: int
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HealthResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    check_id: int = Field(foreign_key="healthcheck.id")
    ok: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    checked_at: datetime = Field(default_factory=datetime.utcnow)


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
