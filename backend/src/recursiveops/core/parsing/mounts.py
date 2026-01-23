from __future__ import annotations

import json


def parse_findmnt(text: str) -> list[dict]:
    if not text.strip():
        return []
    data = json.loads(text)
    if isinstance(data, dict):
        return data.get("filesystems", [])
    return []
