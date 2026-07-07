from datetime import datetime

from app.db.supabase_client import get_supabase_client
from app.schemas.users import User


async def get_or_create_user_github(github_id: str = None, username: str = None, avatar_url: str = None, email: str = None, display_name: str = None):
    supabase = await get_supabase_client()
    existing = await supabase.table("users").select("*").eq("github_id", github_id).execute()
    if existing.data:
        return User.model_validate(existing.data[0])

    email_owner = await supabase.table("users").select("*").eq("email", email).execute()
    if email_owner.data:
        linked = await supabase.table("users").update({
            "github_id": github_id,
            "username": username,
            "avatar_url": email_owner.data[0].get("avatar_url") or avatar_url,
            "display_name": email_owner.data[0].get("display_name") or display_name or username,
        }).eq("id", email_owner.data[0]["id"]).execute()
        return User.model_validate(linked.data[0])

    new_user = await supabase.table("users").insert({
        "github_id": github_id,
        "username": username,
        "display_name": display_name if display_name else username,
        "avatar_url": avatar_url,
        "email": email,
        "created_at": datetime.now().timestamp(),
    }).execute()
    return User.model_validate(new_user.data[0])

async def get_or_create_user_google(google_id, avatar_url: str = None, email: str = None, display_name: str = None):
    supabase = await get_supabase_client()
    existing = await supabase.table("users").select("*").eq("google_id", google_id).execute()
    if existing.data:
        return User.model_validate(existing.data[0])

    email_owner = await supabase.table("users").select("*").eq("email", email).execute()
    if email_owner.data:
        linked = await supabase.table("users").update({
            "google_id": google_id,
            "avatar_url": email_owner.data[0].get("avatar_url") or avatar_url,
            "display_name": email_owner.data[0].get("display_name") or display_name,
        }).eq("id", email_owner.data[0]["id"]).execute()
        return User.model_validate(linked.data[0])

    new_user = await supabase.table("users").insert({
        "google_id": google_id,
        "display_name": display_name if display_name else None,
        "avatar_url": avatar_url,
        "email": email,
        "created_at": datetime.now().timestamp(),
    }).execute()
    return User.model_validate(new_user.data[0])

async def get_user_by_id(user_id: str) -> User | None:
    if user_id is None:
        return None
    supabase = await get_supabase_client()
    user_data = await supabase.table("users").select("*").eq("id", user_id).execute()
    if not user_data.data:
        return None
    return User.model_validate(user_data.data[0])
