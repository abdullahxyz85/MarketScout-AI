from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


class User(BaseModel):
    id: str
    github_id: str | None = None
    email: str
    display_name: str | None = None
    avatar_url: str | None = None
    created_at: float | None = Field(default_factory=lambda: datetime.now().timestamp())

    @model_validator(mode="before")
    @classmethod
    def set_timestamps(cls, values: any) -> any:
        if isinstance(values, dict):
            now = datetime.now().timestamp()
            values.setdefault("created_at", now)
        return values