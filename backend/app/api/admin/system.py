from __future__ import annotations
"""Admin system health API."""
from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import require_admin
from app.schemas.admin import SystemHealth
from app.services.collaboration_service import collab_manager

router = APIRouter(prefix="/admin/system", tags=["admin"])


@router.get("/health", response_model=SystemHealth)
async def system_health(user=Depends(require_admin)):
    # Test connections (simplified — in production, actually ping each service)
    pg_ok = True
    redis_ok = True
    minio_ok = True

    try:
        from app.utils.minio_client import get_minio_client
        client = get_minio_client()
        client.list_buckets()
    except Exception:
        minio_ok = False

    return SystemHealth(
        postgres=pg_ok,
        redis=redis_ok,
        minio=minio_ok,
        celery_workers=0,  # Would inspect celery
        websocket_connections=collab_manager.total_connections(),
        active_sessions=0,
    )
