from __future__ import annotations

from recursiveops.settings import Settings


def actions_allowed(settings: Settings) -> bool:
    return settings.security.allow_actions
