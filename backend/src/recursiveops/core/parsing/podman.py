from __future__ import annotations

import json


def parse_podman_ps(text: str) -> list[dict]:
    if not text.strip():
        return []
    data = json.loads(text)
    if isinstance(data, list):
        return data
    return []
