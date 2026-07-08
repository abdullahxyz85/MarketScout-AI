from supabase import create_async_client, AsyncClient
from app.config import settings


async def get_supabase_client() -> AsyncClient:
    return await create_async_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

