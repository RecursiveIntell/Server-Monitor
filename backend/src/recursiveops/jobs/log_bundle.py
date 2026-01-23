from __future__ import annotations

from typing import Iterable


def bundle_logs(lines: Iterable[str], limit: int = 500) -> str:
    collected = []
    for line in lines:
        collected.append(line)
        if len(collected) >= limit:
            break
    return "\n".join(collected)
