
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings
from app.schemas.users import User


async def create_user_session(user: User) -> JSONResponse:
    max_age = 60 * 60 * 24 * 30
    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=max_age),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    response = JSONResponse({
        "id": str(user.id),
        "github_id": user.github_id,
        "email": user.email,
        "name": user.display_name,
        "picture": user.avatar_url,
        "redirect_url": "/dashboard",
    })
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=max_age,
        path="/",
    )
    return response
    

async def get_user_id_from_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    return payload.get("sub")
