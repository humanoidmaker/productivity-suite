from __future__ import annotations
"""Sharing logic — share with users, share links, permission management."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.share import Share
from app.models.user import User
from app.utils.file_utils import generate_share_token
from app.utils.hashing import hash_password, verify_password


async def share_with_user(db: AsyncSession, file_type: str, file_id: uuid.UUID, shared_by: uuid.UUID, email: str, permission: str = "view") -> Share:
    # Find user by email
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()

    share = Share(
        file_type=file_type, file_id=file_id, shared_by=shared_by,
        shared_with_user_id=user.id if user else None,
        shared_with_email=email.lower(),
        permission=permission,
    )
    db.add(share)
    await db.flush()
    return share


async def create_share_link(db: AsyncSession, file_type: str, file_id: uuid.UUID, shared_by: uuid.UUID, permission: str = "view", password: str | None = None, expires_at: datetime | None = None) -> Share:
    token = generate_share_token()
    share = Share(
        file_type=file_type, file_id=file_id, shared_by=shared_by,
        share_token=token, permission=permission, expires_at=expires_at,
        password_hash=hash_password(password) if password else None,
    )
    db.add(share)
    await db.flush()
    return share


async def get_share_by_token(db: AsyncSession, token: str) -> Share | None:
    result = await db.execute(select(Share).where(Share.share_token == token))
    share = result.scalar_one_or_none()
    if share and share.expires_at and share.expires_at < datetime.now(timezone.utc):
        return None
    return share


async def verify_share_password(share: Share, password: str) -> bool:
    if not share.password_hash:
        return True
    return verify_password(password, share.password_hash)


async def list_shares_for_file(db: AsyncSession, file_type: str, file_id: uuid.UUID) -> list[Share]:
    result = await db.execute(select(Share).where(Share.file_type == file_type, Share.file_id == file_id))
    return list(result.scalars().all())


async def list_shared_with_user(db: AsyncSession, user_id: uuid.UUID) -> list[Share]:
    result = await db.execute(select(Share).where(Share.shared_with_user_id == user_id).order_by(Share.created_at.desc()))
    return list(result.scalars().all())


async def update_share_permission(db: AsyncSession, share: Share, permission: str) -> Share:
    share.permission = permission
    await db.flush()
    return share


async def revoke_share(db: AsyncSession, share: Share) -> None:
    await db.delete(share)
    await db.flush()
