from __future__ import annotations

from app.db.supabase_client import get_supabase_client
from app.schemas.competitors import Competitor


async def create_competitors(rows: list[dict]) -> list[Competitor]:
    if not rows:
        return []
    supabase = await get_supabase_client()
    created = await supabase.table("competitors").insert(rows).execute()
    return [Competitor.model_validate(row) for row in created.data]


async def list_competitors(user_id: str) -> list[Competitor]:
    supabase = await get_supabase_client()
    result = await (
        supabase.table("competitors")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return [Competitor.model_validate(row) for row in result.data]


async def list_competitors_for_report(report_id: str) -> list[Competitor]:
    supabase = await get_supabase_client()
    result = await (
        supabase.table("competitors")
        .select("*")
        .eq("report_id", report_id)
        .execute()
    )
    return [Competitor.model_validate(row) for row in result.data]
