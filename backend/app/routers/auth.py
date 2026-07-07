from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.config import settings
from app.db.users import get_or_create_user
from app.dependencies.auth import create_user_session

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth = OAuth()

oauth.register(
    name="github",
    client_id=settings.OAUTH_GITHUB_CLIENT_ID,
    client_secret=settings.OAUTH_GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",

    api_base_url="https://api.github.com/",
    client_kwargs={
        "scope": "user:email read:user"
    },
)

@router.get("/github/login")
async def github_login(request: Request):
    redirect_uri = f"{settings.FRONTEND_DOMAIN.rstrip('/')}/callback/github"
    return await oauth.github.authorize_redirect(
        request,
        redirect_uri,
    )

@router.get("/github/callback")
async def github_callback(
    request: Request,
):
    try:
        token = await oauth.github.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"github OAuth failed: {exc.error}",
        ) from exc
    response_userinfo = await oauth.github.get("user", token=token)
    response_userinfo.raise_for_status()
    userinfo = response_userinfo.json()
    response_email = await oauth.github.get("user/emails", token=token)
    response_email.raise_for_status()
    emails = response_email.json()
    email = next((e["email"]for e in emails if e["primary"] and e["verified"]),None)

    github_id = str(userinfo.get("id")) if userinfo.get("id") is not None else None
    if github_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="github did not return github id")
    if email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Primary verified email not found")
    
    user = await get_or_create_user(github_id=github_id, username=userinfo.get("login"), avatar_url=userinfo.get("avatar_url"), email=email, display_name=userinfo.get("name"))
    if user is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This email is already linked to another github account")

    return await create_user_session(user=user)


@router.post("/logout")
async def logout():
    response = JSONResponse({"status": "ok"})
    response.delete_cookie(key="access_token", path="/")
    return response