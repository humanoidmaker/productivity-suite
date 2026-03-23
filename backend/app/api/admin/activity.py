from __future__ import annotations
"""Admin activity log API."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import require_admin
from app.services.activity_service import list_activity

router = APIRouter(prefix="/admin/activity", tags=["admin"])


@router.get("")
async def get_activity_log(offset: int = 0, limit: int = Query(50, le=200), user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    entries = await list_activity(db, offset=offset, limit=limit)
    return [{"id": e.id, "user_id": e.user_id, "action": e.action, "file_type": e.file_type, "file_id": e.file_id, "details": e.details_json, "ip_address": e.ip_address, "created_at": e.created_at} for e in entries]
