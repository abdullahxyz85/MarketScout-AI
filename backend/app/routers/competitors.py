from __future__ import annotations

from fastapi import APIRouter, Depends

from app.db.competitors import list_competitors
from app.routers.users import get_current_user
from app.schemas.competitors import Competitor
from app.schemas.users import User

router = APIRouter(prefix="/api/competitors", tags=["competitors"])


@router.get("", response_model=list[Competitor], summary="List tracked competitors for the current user")
async def get_competitors(current_user: User = Depends(get_current_user)):
    return await list_competitors(current_user.id)
