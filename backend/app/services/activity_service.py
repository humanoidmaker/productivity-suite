from __future__ import annotations
"""Activity logging."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog


async def log_activity(db: AsyncSession, user_id: uuid.UUID | None, action: str, file_type: str | None = None, file_id: uuid.UUID | None = None, details: dict | None = None, ip_address: str | None = None) -> ActivityLog:
    entry = ActivityLog(user_id=user_id, action=action, file_type=file_type, file_id=file_id, details_json=details, ip_address=ip_address)
    db.add(entry)
    await db.flush()
    return entry


async def list_activity(db: AsyncSession, user_id: uuid.UUID | None = None, file_type: str | None = None, file_id: uuid.UUID | None = None, offset: int = 0, limit: int = 50) -> list[ActivityLog]:
    q = select(ActivityLog)
    if user_id:
        q = q.where(ActivityLog.user_id == user_id)
    if file_type:
        q = q.where(ActivityLog.file_type == file_type)
    if file_id:
        q = q.where(ActivityLog.file_id == file_id)
    result = await db.execute(q.order_by(ActivityLog.created_at.desc()).offset(offset).limit(limit))
    return list(result.scalars().all())
