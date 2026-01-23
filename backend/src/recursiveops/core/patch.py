from __future__ import annotations

import difflib
import os
import tempfile
from pathlib import Path

import yaml


def validate_yaml(text: str) -> None:
    try:
        yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError("Invalid YAML") from exc


def preview_unified_diff(old_text: str, new_text: str, filename: str) -> str:
    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=filename,
        tofile=filename,
    )
    return "".join(diff)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
        dir=path.parent,
        prefix=f".{path.name}.",
    ) as temp_file:
        temp_file.write(content)
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_name = temp_file.name
    os.replace(temp_name, path)


def apply_yaml_patch(path: Path, new_text: str) -> str:
    validate_yaml(new_text)
    old_text = path.read_text() if path.exists() else ""
    diff = preview_unified_diff(old_text, new_text, str(path))
    atomic_write(path, new_text)
    validate_yaml(path.read_text())
    return diff
