from __future__ import annotations

from app.db.supabase_client import get_supabase_client
from app.schemas.research import ResearchRun


async def create_research_run(**fields) -> ResearchRun:
    supabase = await get_supabase_client()
    created = await supabase.table("research_runs").insert(fields).execute()
    return ResearchRun.model_validate(created.data[0])


async def get_research_run(run_id: str, user_id: str) -> ResearchRun | None:
    supabase = await get_supabase_client()
    result = await (
        supabase.table("research_runs")
        .select("*")
        .eq("id", run_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        return None
    return ResearchRun.model_validate(result.data[0])


async def update_research_run(run_id: str, **fields) -> ResearchRun | None:
    import time

    supabase = await get_supabase_client()
    fields["updated_at"] = time.time()
    result = await (
        supabase.table("research_runs")
        .update(fields)
        .eq("id", run_id)
        .execute()
    )
    if not result.data:
        return None
    return ResearchRun.model_validate(result.data[0])
