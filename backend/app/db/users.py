from datetime import datetime

from app.db.supabase_client import get_supabase_client
from app.schemas.users import User


async def get_or_create_user(github_id: str, username: str, avatar_url: str = None, email: str = None, display_name: str = None):
    supabase = await get_supabase_client()
    existing = await supabase.table("users").select("*").eq("github_id", github_id).execute()
    if existing.data:
        return User.model_validate(existing.data[0])

    email_owner = await supabase.table("users").select("id").eq("email", email).execute()
    if email_owner.data:
        return None

    new_user = await supabase.table("users").insert({
        "github_id": github_id,
        "username": username,
        "display_name": display_name if display_name else username,
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
