from __future__ import annotations
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.share import Share


async def get_user_permission(
    db: AsyncSession,
    user_id: uuid.UUID,
    file_type: str,
    file_id: uuid.UUID,
    owner_id: uuid.UUID,
) -> str | None:
    """
    Returns the effective permission for a user on a file.
    Returns "owner" if user owns the file, or the share permission, or None if no access.
    """
    if user_id == owner_id:
        return "owner"

    result = await db.execute(
        select(Share.permission)
        .where(Share.file_type == file_type)
        .where(Share.file_id == file_id)
        .where(Share.shared_with_user_id == user_id)
    )
    share = result.scalar_one_or_none()
    return share


def can_view(permission: str | None) -> bool:
    return permission in ("owner", "view", "comment", "edit")


def can_comment(permission: str | None) -> bool:
    return permission in ("owner", "comment", "edit")


def can_edit(permission: str | None) -> bool:
    return permission in ("owner", "edit")


def is_owner(permission: str | None) -> bool:
    return permission == "owner"


def is_admin_role(role: str) -> bool:
    return role in ("admin", "superadmin")
