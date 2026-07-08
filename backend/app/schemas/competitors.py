from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class Competitor(BaseModel):
    id: str
    user_id: str
    report_id: str | None = None
    name: str
    segment: str | None = None
    market_share: float | None = None
    threat: str | None = None
    trend: str | None = None
    revenue: str | None = None
    created_at: float | None = Field(default_factory=lambda: datetime.now().timestamp())

    @model_validator(mode="before")
    @classmethod
    def set_timestamps(cls, values: any) -> any:
        if isinstance(values, dict):
            now = datetime.now().timestamp()
            values.setdefault("created_at", now)
        return values
