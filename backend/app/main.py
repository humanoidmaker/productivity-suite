import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
)

# Middleware (order matters — outermost first)
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}


# Register API routers
from app.api.auth import router as auth_router  # noqa: E402
from app.api.folders import router as folders_router  # noqa: E402
from app.api.documents import router as documents_router  # noqa: E402
from app.api.spreadsheets import router as spreadsheets_router  # noqa: E402
from app.api.presentations import router as presentations_router  # noqa: E402
from app.api.sharing import router as sharing_router  # noqa: E402
from app.api.comments import router as comments_router  # noqa: E402
from app.api.versions import router as versions_router  # noqa: E402
from app.api.assets import router as assets_router  # noqa: E402
from app.api.templates import router as templates_router  # noqa: E402
from app.api.stars import router as stars_router  # noqa: E402
from app.api.recents import router as recents_router  # noqa: E402
from app.api.trash import router as trash_router  # noqa: E402
from app.api.search import router as search_router  # noqa: E402
from app.api.collaboration import router as collab_router  # noqa: E402
from app.api.admin.dashboard import router as admin_dashboard_router  # noqa: E402
from app.api.admin.users import router as admin_users_router  # noqa: E402
from app.api.admin.system import router as admin_system_router  # noqa: E402
from app.api.admin.settings import router as admin_settings_router  # noqa: E402
from app.api.admin.activity import router as admin_activity_router  # noqa: E402

for r in [auth_router, folders_router, documents_router, spreadsheets_router, presentations_router,
          sharing_router, comments_router, versions_router, assets_router, templates_router,
          stars_router, recents_router, trash_router, search_router,
          admin_dashboard_router, admin_users_router, admin_system_router, admin_settings_router, admin_activity_router]:
    app.include_router(r, prefix=settings.api_prefix)

# WebSocket routes (no prefix)
app.include_router(collab_router)


@app.on_event("startup")
async def on_startup():
    logging.getLogger("productivity").info("Productivity Suite API starting up")
    # Ensure MinIO buckets exist
    try:
        from app.utils.minio_client import ensure_buckets
        ensure_buckets()
    except Exception as e:
        logging.getLogger("productivity").warning("MinIO bucket init failed (will retry): %s", e)


@app.on_event("shutdown")
async def on_shutdown():
    logging.getLogger("productivity").info("Productivity Suite API shutting down")
    from app.database import engine
    await engine.dispose()
