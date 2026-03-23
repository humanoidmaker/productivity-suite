from __future__ import annotations
"""Presentation CRUD and slide management."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.presentation import Presentation


DEFAULT_THEME = {
    "primary": "#2563eb",
    "secondary": "#64748b",
    "accent": "#f59e0b",
    "background": "#ffffff",
    "text": "#1e293b",
    "headingFont": "Inter, system-ui, sans-serif",
    "bodyFont": "Inter, system-ui, sans-serif",
}

DEFAULT_SLIDES_META = {
    "slides": [
        {"id": "slide-1", "layout": "title", "transition": "none", "transitionDuration": 0.5, "speakerNotes": "", "hidden": False}
    ],
}


async def create_presentation(db: AsyncSession, owner_id: uuid.UUID, title: str = "Untitled Presentation", folder_id: uuid.UUID | None = None, aspect_ratio: str = "16:9") -> Presentation:
    pres = Presentation(
        title=title, owner_id=owner_id, folder_id=folder_id,
        aspect_ratio=aspect_ratio, theme_json=DEFAULT_THEME, slides_meta_json=DEFAULT_SLIDES_META,
    )
    db.add(pres)
    await db.flush()
    return pres


async def get_presentation(db: AsyncSession, pres_id: uuid.UUID) -> Presentation | None:
    result = await db.execute(select(Presentation).where(Presentation.id == pres_id))
    return result.scalar_one_or_none()


async def list_presentations(db: AsyncSession, owner_id: uuid.UUID, folder_id: uuid.UUID | None = None, offset: int = 0, limit: int = 20) -> tuple[list[Presentation], int]:
    base = select(Presentation).where(Presentation.owner_id == owner_id, Presentation.is_trashed == False)
    if folder_id is not None:
        base = base.where(Presentation.folder_id == folder_id)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    items = (await db.execute(base.order_by(Presentation.updated_at.desc()).offset(offset).limit(limit))).scalars().all()
    return list(items), total


async def update_presentation_meta(db: AsyncSession, pres: Presentation, title: str | None = None, folder_id: uuid.UUID | None = ..., slides_meta: dict | None = None, theme: dict | None = None, aspect_ratio: str | None = None) -> Presentation:
    if title is not None:
        pres.title = title
    if folder_id is not ...:
        pres.folder_id = folder_id
    if slides_meta is not None:
        pres.slides_meta_json = slides_meta
        pres.slide_count = len(slides_meta.get("slides", []))
    if theme is not None:
        pres.theme_json = theme
    if aspect_ratio is not None:
        pres.aspect_ratio = aspect_ratio
    pres.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return pres


async def update_presentation_content(db: AsyncSession, pres: Presentation, slides_yjs: bytes | None = None, editor_id: uuid.UUID | None = None) -> Presentation:
    if slides_yjs is not None:
        pres.slides_yjs = slides_yjs
    if editor_id:
        pres.last_edited_by = editor_id
    pres.last_edited_at = datetime.now(timezone.utc)
    await db.flush()
    return pres


async def duplicate_presentation(db: AsyncSession, pres: Presentation, new_owner_id: uuid.UUID | None = None) -> Presentation:
    new_pres = Presentation(
        title=f"{pres.title} (Copy)",
        owner_id=new_owner_id or pres.owner_id,
        folder_id=pres.folder_id,
        slides_yjs=pres.slides_yjs,
        slides_meta_json=pres.slides_meta_json,
        slide_count=pres.slide_count,
        theme_json=pres.theme_json,
        aspect_ratio=pres.aspect_ratio,
    )
    db.add(new_pres)
    await db.flush()
    return new_pres


async def soft_delete_presentation(db: AsyncSession, pres: Presentation) -> None:
    pres.is_trashed = True
    pres.trashed_at = datetime.now(timezone.utc)
    await db.flush()


async def restore_presentation(db: AsyncSession, pres: Presentation) -> None:
    pres.is_trashed = False
    pres.trashed_at = None
    await db.flush()


async def permanent_delete_presentation(db: AsyncSession, pres: Presentation) -> None:
    await db.delete(pres)
    await db.flush()
