from __future__ import annotations
"""Recents API — list recently accessed files."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.models.recent_file import RecentFile

router = APIRouter(prefix="/recents", tags=["recents"])


@router.get("", response_model=list[dict])
async def list_recents(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RecentFile).where(RecentFile.user_id == user.id).order_by(RecentFile.accessed_at.desc()).limit(50)
    )
    recents = result.scalars().all()
    return [{"file_type": r.file_type, "file_id": r.file_id, "accessed_at": r.accessed_at} for r in recents]


async def track_recent(db: AsyncSession, user_id: uuid.UUID, file_type: str, file_id: uuid.UUID) -> None:
    """Upsert a recent file entry."""
    # Remove existing entry
    await db.execute(delete(RecentFile).where(RecentFile.user_id == user_id, RecentFile.file_type == file_type, RecentFile.file_id == file_id))
    # Add new
    db.add(RecentFile(user_id=user_id, file_type=file_type, file_id=file_id, accessed_at=datetime.now(timezone.utc)))
    # Trim to 50
    result = await db.execute(
        select(RecentFile.id).where(RecentFile.user_id == user_id).order_by(RecentFile.accessed_at.desc()).offset(50)
    )
    old_ids = [r[0] for r in result.all()]
    if old_ids:
        await db.execute(delete(RecentFile).where(RecentFile.id.in_(old_ids)))
    await db.flush()
