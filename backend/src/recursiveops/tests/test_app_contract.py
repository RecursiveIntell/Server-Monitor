import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from recursiveops.auth.models import User
from recursiveops.auth.security import hash_password
from recursiveops.main import create_app
from recursiveops.settings import load_settings


@pytest.fixture()
def settings_file(tmp_path: Path) -> Path:
    jwt_secret = tmp_path / "jwt.secret"
    jwt_secret.write_text("test-secret")

    config = tmp_path / "config.yml"
    config.write_text(
        """
server:
  bind_host: "127.0.0.1"
  bind_port: 8844

paths:
  cloudflared_config: "/etc/cloudflared/config.yml"
  fstab: "/etc/fstab"

systemd:
  cloudflared_unit: "cloudflared.service"
  extra_units: []

security:
  jwt_secret_file: "{secret}"
  allow_actions: true
  require_login: true

checks:
  default_interval_seconds: 60
  http_timeout_seconds: 5
  log_tail_lines: 250

llm:
  enabled: false
  provider: "ollama"
  ollama:
    base_url: "http://127.0.0.1:11434"
    model: "qwen2.5:7b"
  cloud:
    enabled: false
    provider: "stub"
""".format(secret=str(jwt_secret))
    )
    return config


def test_app_contract(settings_file: Path, tmp_path: Path) -> None:
    settings = load_settings(settings_file)
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = User(
            username="admin",
            hashed_password=hash_password("changeme"),
            is_active=True,
            is_admin=True,
        )
        session.add(user)
        session.commit()

    app = create_app(settings=settings, engine=engine)
    client = TestClient(app)

    login = client.post("/api/auth/login", json={"username": "admin", "password": "changeme"})
    assert login.status_code == 200
    payload = login.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]

    headers = {"Authorization": f"Bearer {payload['access_token']}"}
    health = client.get("/api/health", headers=headers)
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    settings_resp = client.get("/api/settings", headers=headers)
    assert settings_resp.status_code == 200
    data = settings_resp.json()
    assert data["server"]["bind_host"] == "127.0.0.1"
    assert data["checks"]["http_timeout_seconds"] == 5
    assert data["security"]["require_login"] is True
