from __future__ import annotations

from app.db.supabase_client import get_supabase_client
from app.schemas.reports import Report


async def create_report(**fields) -> Report:
    supabase = await get_supabase_client()
    created = await supabase.table("reports").insert(fields).execute()
    return Report.model_validate(created.data[0])


async def list_reports(user_id: str) -> list[Report]:
    supabase = await get_supabase_client()
    result = await (
        supabase.table("reports")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return [Report.model_validate(row) for row in result.data]


async def get_report(report_id: str, user_id: str) -> Report | None:
    supabase = await get_supabase_client()
    result = await (
        supabase.table("reports")
        .select("*")
        .eq("id", report_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        return None
    return Report.model_validate(result.data[0])


async def set_starred(report_id: str, user_id: str, starred: bool) -> Report | None:
    supabase = await get_supabase_client()
    result = await (
        supabase.table("reports")
        .update({"starred": starred})
        .eq("id", report_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        return None
    return Report.model_validate(result.data[0])


async def delete_report(report_id: str, user_id: str) -> bool:
    supabase = await get_supabase_client()
    result = await (
        supabase.table("reports")
        .delete()
        .eq("id", report_id)
        .eq("user_id", user_id)
        .execute()
    )
    return bool(result.data)
