from __future__ import annotations
"""Soft delete, restore, auto-purge trash."""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.spreadsheet import Spreadsheet
from app.models.presentation import Presentation
from app.models.folder import Folder

FILE_MODELS = {"document": Document, "spreadsheet": Spreadsheet, "presentation": Presentation, "folder": Folder}


async def list_trash(db: AsyncSession, owner_id: uuid.UUID) -> dict:
    """List all trashed items for a user."""
    result = {}
    for file_type, model in FILE_MODELS.items():
        q = select(model).where(model.owner_id == owner_id, model.is_trashed == True).order_by(model.trashed_at.desc())
        items = (await db.execute(q)).scalars().all()
        result[file_type + "s"] = list(items)
    return result


async def restore_item(db: AsyncSession, file_type: str, file_id: uuid.UUID) -> bool:
    model = FILE_MODELS.get(file_type)
    if not model:
        return False
    result = await db.execute(select(model).where(model.id == file_id))
    item = result.scalar_one_or_none()
    if not item:
        return False
    item.is_trashed = False
    item.trashed_at = None
    await db.flush()
    return True


async def permanent_delete_item(db: AsyncSession, file_type: str, file_id: uuid.UUID) -> bool:
    model = FILE_MODELS.get(file_type)
    if not model:
        return False
    result = await db.execute(select(model).where(model.id == file_id, model.is_trashed == True))
    item = result.scalar_one_or_none()
    if not item:
        return False
    await db.delete(item)
    await db.flush()
    return True


async def empty_trash(db: AsyncSession, owner_id: uuid.UUID) -> int:
    """Permanently delete all trashed items. Returns count deleted."""
    total = 0
    for model in FILE_MODELS.values():
        result = await db.execute(select(model).where(model.owner_id == owner_id, model.is_trashed == True))
        items = result.scalars().all()
        for item in items:
            await db.delete(item)
            total += 1
    await db.flush()
    return total


async def purge_old_trash(db: AsyncSession, days: int = 30) -> int:
    """Auto-purge trash items older than N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    total = 0
    for model in FILE_MODELS.values():
        result = await db.execute(select(model).where(model.is_trashed == True, model.trashed_at < cutoff))
        items = result.scalars().all()
        for item in items:
            await db.delete(item)
            total += 1
    await db.flush()
    return total
