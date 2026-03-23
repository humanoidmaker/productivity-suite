from __future__ import annotations
"""Storage quota tracking and enforcement."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.asset import Asset
from sqlalchemy import func


async def get_storage_used(db: AsyncSession, user_id: uuid.UUID) -> int:
    """Calculate total storage used by a user (from assets)."""
    result = await db.execute(
        select(func.coalesce(func.sum(Asset.size), 0)).where(Asset.owner_id == user_id)
    )
    return result.scalar() or 0


async def refresh_storage_used(db: AsyncSession, user_id: uuid.UUID) -> int:
    """Recalculate and update user's storage_used field."""
    used = await get_storage_used(db, user_id)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.storage_used = used
        await db.flush()
    return used


async def check_quota(db: AsyncSession, user_id: uuid.UUID, additional_bytes: int = 0) -> bool:
    """Check if user has enough quota for additional_bytes."""
    result = await db.execute(select(User.storage_used, User.storage_quota).where(User.id == user_id))
    row = result.one_or_none()
    if not row:
        return False
    used, quota = row
    return (used + additional_bytes) <= quota


async def update_quota(db: AsyncSession, user_id: uuid.UUID, new_quota_bytes: int) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.storage_quota = new_quota_bytes
        await db.flush()
