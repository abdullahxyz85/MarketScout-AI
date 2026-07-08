from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import competitors, dashboard, healthcare, reports, research, users
from app.routers.auth import github, google


app = FastAPI(title="MarketScout-AI", version="0.1.0", docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json")

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

app.include_router(github.router)
app.include_router(google.router)
app.include_router(users.router)
app.include_router(research.router)
app.include_router(reports.router)
app.include_router(competitors.router)
app.include_router(dashboard.router)
app.include_router(healthcare.router)


@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
