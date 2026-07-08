from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class Report(BaseModel):
    id: str
    user_id: str
    research_run_id: str | None = None
    title: str
    description: str | None = None
    industry: str | None = None
    healthcare_mode: bool = False
    score: float = 0
    opportunity_score: float = 0
    risk_level: str | None = None
    pages: int = 1
    starred: bool = False
    chart_data: dict = Field(default_factory=dict)
    created_at: float | None = Field(default_factory=lambda: datetime.now().timestamp())

    @model_validator(mode="before")
    @classmethod
    def set_timestamps(cls, values: any) -> any:
        if isinstance(values, dict):
            now = datetime.now().timestamp()
            values.setdefault("created_at", now)
        return values


class ReportListItem(BaseModel):
    id: str
    title: str
    industry: str | None = None
    score: float = 0
    pages: int = 1
    starred: bool = False
    created_at: float


class ReportDetail(Report):
    pass
