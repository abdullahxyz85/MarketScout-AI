from __future__ import annotations

from typing import List, Optional, TypedDict


class ResearchState(TypedDict):
    job_id: str
    idea: str
    industry: str
    healthcare_mode: bool
    progress: int
    current_agent: str
    errors: List[str]
    research: Optional[dict]
    competitors: Optional[dict]
    scientific: Optional[dict]
    patents: Optional[dict]
    funding: Optional[dict]
    trends: Optional[dict]
    research_gaps: Optional[dict]
    swot: Optional[dict]
    opportunities: Optional[dict]
    risks: Optional[dict]
    innovation_score: Optional[dict]
    validation: Optional[dict]
    strategy: Optional[dict]
    knowledge_graph: Optional[dict]
    report: Optional[dict]
