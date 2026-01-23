from __future__ import annotations

from sqlmodel import SQLModel, create_engine

from recursiveops.settings import Settings


def get_engine(settings: Settings):
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(settings.database_url, connect_args=connect_args)


def init_db(engine) -> None:
    SQLModel.metadata.create_all(engine)
