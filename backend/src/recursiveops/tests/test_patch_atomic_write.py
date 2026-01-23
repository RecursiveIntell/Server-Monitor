from pathlib import Path

import pytest

from recursiveops.core.patch import apply_yaml_patch, atomic_write


def test_atomic_write_replaces_content(tmp_path: Path) -> None:
    target = tmp_path / "config.yml"
    target.write_text("a: 1\n")

    atomic_write(target, "a: 2\n")

    assert target.read_text() == "a: 2\n"


def test_apply_yaml_patch_rejects_invalid_yaml(tmp_path: Path) -> None:
    target = tmp_path / "config.yml"
    target.write_text("a: 1\n")

    with pytest.raises(ValueError):
        apply_yaml_patch(target, "a: [\n")

    assert target.read_text() == "a: 1\n"
