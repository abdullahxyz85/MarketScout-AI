from __future__ import annotations

import re
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

# Allowed characters for free-text fields (no control chars / null bytes)
_SAFE_TEXT_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

def _reject_control_chars(v: str) -> str:
    if v and _SAFE_TEXT_RE.search(v):
        raise ValueError("Control characters are not allowed.")
    return v


class ResearchRequest(BaseModel):
    """Sensitive model — extra fields are rejected."""
    model_config = {"extra": "forbid"}

    idea: str = Field(..., min_length=10, max_length=1000, description="The startup idea to research")
    industry: str = Field(default="", max_length=100, description="Target industry vertical")
    healthcare_mode: bool = Field(default=False, description="Enable healthcare-specific research mode")

    @field_validator("idea", "industry")
    @classmethod
    def no_control_chars(cls, v: str) -> str:
        return _reject_control_chars(v)


class ScenarioParameter(BaseModel):
    model_config = {"extra": "forbid"}

    pricing_strategy: Optional[str] = Field(default=None, max_length=200)
    target_market: Optional[str] = Field(default=None, max_length=200)
    geography: Optional[str] = Field(default=None, max_length=200)
    technology_choice: Optional[str] = Field(default=None, max_length=200)
    team_size: Optional[str] = Field(default=None, max_length=100)
    funding_amount: Optional[str] = Field(default=None, max_length=100)


class ScenarioRequest(BaseModel):
    """Sensitive model — extra fields are rejected. Job ID comes from the URL path only."""
    model_config = {"extra": "forbid"}

    scenario: ScenarioParameter


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: str


class ProgressEvent(BaseModel):
    progress: int
    current_agent: str
    done: bool
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class AskRequest(BaseModel):
    """Sensitive model — extra fields are rejected."""
    model_config = {"extra": "forbid"}

    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Question about the research results",
    )

    @field_validator("question")
    @classmethod
    def no_control_chars(cls, v: str) -> str:
        return _reject_control_chars(v)
