from __future__ import annotations
"""Admin settings API."""
from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import require_admin
from app.schemas.admin import SystemSettings
from app.config import get_settings

router = APIRouter(prefix="/admin/settings", tags=["admin"])


@router.get("", response_model=SystemSettings)
async def get_system_settings(user=Depends(require_admin)):
    s = get_settings()
    return SystemSettings(
        default_storage_quota_mb=s.default_storage_quota_mb,
        max_file_size_mb=s.max_file_size_mb,
        max_collaborators_per_file=s.max_collaborators_per_file,
        auto_save_interval_seconds=s.auto_save_interval_seconds,
        version_snapshot_interval_minutes=s.version_snapshot_interval_minutes,
        max_versions_per_file=s.max_versions_per_file,
        trash_auto_purge_days=s.trash_auto_purge_days,
        registration_enabled=s.registration_enabled,
        rate_limit_per_minute=s.rate_limit_per_minute,
    )
