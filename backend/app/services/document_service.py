from __future__ import annotations
"""Document CRUD and content management."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


DEFAULT_PAGE_SETTINGS = {
    "size": "A4",
    "orientation": "portrait",
    "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1},
}


async def create_document(db: AsyncSession, owner_id: uuid.UUID, title: str = "Untitled Document", folder_id: uuid.UUID | None = None) -> Document:
    doc = Document(title=title, owner_id=owner_id, folder_id=folder_id, page_settings_json=DEFAULT_PAGE_SETTINGS)
    db.add(doc)
    await db.flush()
    return doc


async def get_document(db: AsyncSession, doc_id: uuid.UUID) -> Document | None:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    return result.scalar_one_or_none()


async def list_documents(db: AsyncSession, owner_id: uuid.UUID, folder_id: uuid.UUID | None = None, offset: int = 0, limit: int = 20) -> tuple[list[Document], int]:
    base = select(Document).where(Document.owner_id == owner_id, Document.is_trashed == False)
    if folder_id is not None:
        base = base.where(Document.folder_id == folder_id)
    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    items = (await db.execute(base.order_by(Document.updated_at.desc()).offset(offset).limit(limit))).scalars().all()
    return list(items), total


async def update_document_meta(db: AsyncSession, doc: Document, title: str | None = None, folder_id: uuid.UUID | None = ..., page_settings: dict | None = None) -> Document:
    if title is not None:
        doc.title = title
    if folder_id is not ...:
        doc.folder_id = folder_id
    if page_settings is not None:
        doc.page_settings_json = page_settings
    doc.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return doc


async def update_document_content(db: AsyncSession, doc: Document, content_html: str | None = None, content_yjs: bytes | None = None, editor_id: uuid.UUID | None = None) -> Document:
    if content_html is not None:
        doc.content_html = content_html
        # Update word/char count
        import re
        text = re.sub(r"<[^>]+>", " ", content_html)
        words = text.split()
        doc.word_count = len(words)
        doc.char_count = len(text.replace(" ", ""))
    if content_yjs is not None:
        doc.content_yjs = content_yjs
    if editor_id:
        doc.last_edited_by = editor_id
    doc.last_edited_at = datetime.now(timezone.utc)
    await db.flush()
    return doc


async def duplicate_document(db: AsyncSession, doc: Document, new_owner_id: uuid.UUID | None = None) -> Document:
    new_doc = Document(
        title=f"{doc.title} (Copy)",
        owner_id=new_owner_id or doc.owner_id,
        folder_id=doc.folder_id,
        content_yjs=doc.content_yjs,
        content_html=doc.content_html,
        word_count=doc.word_count,
        char_count=doc.char_count,
        page_settings_json=doc.page_settings_json,
    )
    db.add(new_doc)
    await db.flush()
    return new_doc


async def soft_delete_document(db: AsyncSession, doc: Document) -> None:
    doc.is_trashed = True
    doc.trashed_at = datetime.now(timezone.utc)
    await db.flush()


async def restore_document(db: AsyncSession, doc: Document) -> None:
    doc.is_trashed = False
    doc.trashed_at = None
    await db.flush()


async def permanent_delete_document(db: AsyncSession, doc: Document) -> None:
    await db.delete(doc)
    await db.flush()
