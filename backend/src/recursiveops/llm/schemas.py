from __future__ import annotations

from pydantic import BaseModel, Field


class FailureExplanation(BaseModel):
    summary: str
    possible_causes: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)


class DiffExplanation(BaseModel):
    summary: str
    risk_level: str
    notable_changes: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)
