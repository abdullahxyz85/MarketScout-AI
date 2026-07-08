from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ResearchRequest(BaseModel):
    idea: str
    industry: str | None = None
    healthcare_mode: bool = False


class ResearchRun(BaseModel):
    id: str
    user_id: str
    idea: str
    industry: str | None = None
    healthcare_mode: bool = False
    status: str = "pending"
    current_agent: str | None = None
    progress: int = 0
    report_id: str | None = None
    error: str | None = None
    created_at: float | None = Field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float | None = Field(default_factory=lambda: datetime.now().timestamp())

    @model_validator(mode="before")
    @classmethod
    def set_timestamps(cls, values: any) -> any:
        if isinstance(values, dict):
            now = datetime.now().timestamp()
            values.setdefault("created_at", now)
            values.setdefault("updated_at", now)
        return values


class ResearchStartResponse(BaseModel):
    report_id: str


AGENT_SEQUENCE = [
    "Research Agent",
    "Competitor Agent",
    "Market Agent",
    "Trend Agent",
    "SWOT Agent",
    "Opportunity Agent",
    "Risk Agent",
    "Report Generator",
]


class CompetitorFinding(BaseModel):
    name: str
    segment: str | None = None
    market_share: float = 0
    threat: str = "medium"
    trend: str = "stable"
    revenue: str | None = None


class SwotResult(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    threats: list[str] = Field(default_factory=list)


class TrendPoint(BaseModel):
    month: str
    score: float
    opportunity: float
    risk: float


class MarketResult(BaseModel):
    tam: str = "N/A"
    market_score: float = 0
    funding_by_sector: list[dict] = Field(default_factory=list)


class OpportunityResult(BaseModel):
    opportunity_score: float = 0
    highlights: list[str] = Field(default_factory=list)


class RiskResult(BaseModel):
    risk_level: str = "Medium"
    risk_score: float = 0
    risks: list[str] = Field(default_factory=list)


class ReportSummary(BaseModel):
    title: str
    description: str
