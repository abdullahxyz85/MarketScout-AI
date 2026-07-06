from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import auth, users


app = FastAPI(title="MarketScout-AI", version="0.1.0", docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json")

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
