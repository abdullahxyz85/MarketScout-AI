from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.schemas.users import User
from app.db.users import get_user_by_id
from app.dependencies.auth import get_user_id_from_token

router = APIRouter(prefix="/api/users", tags=["users"])


async def get_current_user(request: Request) -> User:
    token = request.cookies.get("access_token")
    user_id = await get_user_id_from_token(token) if token else None
    user = await get_user_by_id(user_id) if user_id else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


@router.get("/me", response_model=User, summary="Get the current authenticated user")
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
