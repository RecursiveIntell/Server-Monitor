from __future__ import annotations

from typing import Any, Dict


def _deep_merge(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def apply_llm_update(config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    base = dict(config)
    current = base.get("llm") or {}
    base["llm"] = _deep_merge(current, updates)
    return base


def apply_paths_update(config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    base = dict(config)
    current = base.get("paths") or {}
    base["paths"] = _deep_merge(current, updates)
    return base
