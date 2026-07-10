from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    idea: str = Field(..., min_length=10, max_length=4000, description="The startup idea to research")
    industry: str = Field(default="", description="Target industry vertical")
    healthcare_mode: bool = Field(default=False, description="Enable healthcare-specific research mode")
    user_id: Optional[str] = Field(default=None, description="Optional user ID for persistent memory")


class ScenarioParameter(BaseModel):
    pricing_strategy: Optional[str] = Field(default=None)
    target_market: Optional[str] = Field(default=None)
    geography: Optional[str] = Field(default=None)
    technology_choice: Optional[str] = Field(default=None)
    team_size: Optional[str] = Field(default=None)
    funding_amount: Optional[str] = Field(default=None)


class ScenarioRequest(BaseModel):
    base_job_id: str = Field(..., description="Job ID of the base research to simulate against")
    scenario: ScenarioParameter
    user_id: Optional[str] = Field(default=None)


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
    question: str = Field(..., min_length=3, max_length=500, description="Question about the research results")
