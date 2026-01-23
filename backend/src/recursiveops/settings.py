from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from pydantic import BaseModel, Field


class ServerSettings(BaseModel):
    bind_host: str = "127.0.0.1"
    bind_port: int = 8844


class PathsSettings(BaseModel):
    cloudflared_config: str = "/etc/cloudflared/config.yml"
    fstab: str = "/etc/fstab"


class SystemdSettings(BaseModel):
    cloudflared_unit: str = "cloudflared.service"
    extra_units: list[str] = Field(default_factory=list)


class SecuritySettings(BaseModel):
    jwt_secret_file: str = "/etc/recursiveops/jwt.secret"
    allow_actions: bool = True
    require_login: bool = True


class ChecksSettings(BaseModel):
    default_interval_seconds: int = 60
    http_timeout_seconds: int = 5
    log_tail_lines: int = 250


class OllamaSettings(BaseModel):
    base_url: str = "http://127.0.0.1:11434"
    model: str = "qwen2.5:7b"


class CloudSettings(BaseModel):
    enabled: bool = False
    provider: str = "stub"


class LLMSettings(BaseModel):
    enabled: bool = True
    provider: str = "ollama"
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    cloud: CloudSettings = Field(default_factory=CloudSettings)


class Settings(BaseModel):
    server: ServerSettings = Field(default_factory=ServerSettings)
    paths: PathsSettings = Field(default_factory=PathsSettings)
    systemd: SystemdSettings = Field(default_factory=SystemdSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    checks: ChecksSettings = Field(default_factory=ChecksSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    database_url: str = Field(
        default_factory=lambda: os.getenv("RECURSIVEOPS_DB_URL", "sqlite:///./recursiveops.db")
    )
    config_path: str | None = None


def load_settings(path: str | Path) -> Settings:
    config_path = Path(path)
    data: Dict[str, Any] = {}
    if config_path.exists():
        data = yaml.safe_load(config_path.read_text()) or {}
    settings = Settings.parse_obj(data)
    settings.config_path = str(config_path)
    if "database_url" not in data and "RECURSIVEOPS_DB_URL" not in os.environ:
        db_path = config_path.parent / "recursiveops.db"
        settings.database_url = f"sqlite:///{db_path}"
    return settings


_settings_cache: Settings | None = None


def _find_dev_config(start: Path) -> str | None:
    for base in [start, *start.parents]:
        candidate = base / ".secrets" / "config.yml"
        if candidate.exists():
            return str(candidate)
    return None


def get_settings() -> Settings:
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache
    config_path_env = os.getenv("RECURSIVEOPS_CONFIG")
    if config_path_env:
        config_path = config_path_env
    else:
        default_path = Path("/etc/recursiveops/config.yml")
        if default_path.exists():
            config_path = str(default_path)
        else:
            dev_path = _find_dev_config(Path.cwd())
            config_path = dev_path or str(default_path)
    _settings_cache = load_settings(config_path)
    return _settings_cache


def set_settings_cache(settings: Settings) -> None:
    global _settings_cache
    _settings_cache = settings


def public_settings(settings: Settings) -> Dict[str, Any]:
    data = settings.dict()
    data["security"] = {
        "allow_actions": settings.security.allow_actions,
        "require_login": settings.security.require_login,
    }
    data.pop("database_url", None)
    data.pop("config_path", None)
    return data
