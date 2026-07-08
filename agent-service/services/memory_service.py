from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from config import settings


async def _get_client():
    from supabase import acreate_client
    return await acreate_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_SERVICE_KEY,
    )


def _is_configured() -> bool:
    return bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY)


async def save_research_result(
    job_id: str,
    idea: str,
    industry: str,
    user_id: Optional[str],
    result: Dict[str, Any],
) -> bool:
    """Persist a completed research result to Supabase. Returns True on success, False otherwise."""
    if not _is_configured():
        return False
    try:
        client = await _get_client()
        await client.table("agent_research_jobs").insert({
            "job_id": job_id,
            "idea": idea,
            "industry": industry,
            "user_id": user_id,
            "result": json.dumps(result, default=str),
            "innovation_score": (result.get("innovation_score") or {}).get("innovation_score"),
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
        return True
    except Exception as exc:
        print(f"[memory_service] save_research_result failed: {exc}")
        return False


async def get_past_research(industry: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve past research summaries for a given industry.
    Used to provide context (persistent research memory) to new research sessions.
    """
    if not _is_configured():
        return []
    try:
        client = await _get_client()
        response = (
            await client.table("agent_research_jobs")
            .select("idea, industry, result, created_at")
            .eq("industry", industry)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        items = []
        for row in response.data or []:
            try:
                result = json.loads(row["result"])
                items.append({
                    "idea": row["idea"],
                    "industry": row["industry"],
                    "executive_summary": (result.get("report") or {}).get("executive_summary", ""),
                    "innovation_score": (result.get("innovation_score") or {}).get("innovation_score"),
                    "created_at": row["created_at"],
                })
            except Exception:
                continue
        return items
    except Exception:
        return []


async def get_research_result(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a specific research result by job_id from persistent storage."""
    if not _is_configured():
        return None
    try:
        client = await _get_client()
        response = (
            await client.table("agent_research_jobs")
            .select("result")
            .eq("job_id", job_id)
            .limit(1)
            .execute()
        )
        if response.data:
            return json.loads(response.data[0]["result"])
        return None
    except Exception as exc:
        print(f"[memory_service] get_research_result failed: {exc}")
        return None


async def get_user_research_history(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve the research history for a specific user."""
    if not _is_configured():
        return []
    try:
        client = await _get_client()
        response = (
            await client.table("agent_research_jobs")
            .select("job_id, idea, industry, innovation_score, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception:
        return []
