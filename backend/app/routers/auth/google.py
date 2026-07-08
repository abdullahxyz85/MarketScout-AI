from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException, Request, status
from app.config import settings
from app.dependencies.auth import create_user_session
from app.db.users import get_or_create_user_google

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.OAUTH_GOOGLE_CLIENT_ID,
    client_secret=settings.OAUTH_GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    },
)

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = f"{settings.FRONTEND_DOMAIN.rstrip('/')}/callback/google"
    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
    )

@router.get("/google/callback")
async def google_callback(
    request: Request,
):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth failed: {exc.error}",
        ) from exc

    userinfo = token.get("userinfo")
    if not userinfo:
        userinfo = await oauth.google.userinfo(token=token)
    google_id = userinfo.get("sub")
    email = userinfo.get("email")
    if not google_id or not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google did not return sub or email")

    user = await get_or_create_user_google(google_id=google_id, avatar_url=userinfo.get("picture"), email=email, display_name=userinfo.get("name"))
    if user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email is already linked to another Google account")

    return await create_user_session(user=user)
