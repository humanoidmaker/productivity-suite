from __future__ import annotations
"""Full-text search across all file types."""

import uuid

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.spreadsheet import Spreadsheet
from app.models.presentation import Presentation


async def search_files(db: AsyncSession, owner_id: uuid.UUID, query: str, offset: int = 0, limit: int = 20) -> list[dict]:
    """Search documents, spreadsheets, and presentations by title and content."""
    if not query.strip():
        return []

    like_q = f"%{query}%"
    results: list[dict] = []

    # Search documents (title + content_html)
    doc_q = select(Document).where(
        Document.owner_id == owner_id,
        Document.is_trashed == False,
        or_(Document.title.ilike(like_q), Document.content_html.ilike(like_q)),
    ).limit(limit)
    docs = (await db.execute(doc_q)).scalars().all()
    for d in docs:
        snippet = _extract_snippet(d.content_html or "", query) if d.content_html else ""
        results.append({"type": "document", "id": d.id, "title": d.title, "snippet": snippet, "updated_at": d.updated_at})

    # Search spreadsheets (title only — content is binary Yjs)
    sheet_q = select(Spreadsheet).where(
        Spreadsheet.owner_id == owner_id,
        Spreadsheet.is_trashed == False,
        Spreadsheet.title.ilike(like_q),
    ).limit(limit)
    sheets = (await db.execute(sheet_q)).scalars().all()
    for s in sheets:
        results.append({"type": "spreadsheet", "id": s.id, "title": s.title, "snippet": "", "updated_at": s.updated_at})

    # Search presentations (title only)
    pres_q = select(Presentation).where(
        Presentation.owner_id == owner_id,
        Presentation.is_trashed == False,
        Presentation.title.ilike(like_q),
    ).limit(limit)
    presentations = (await db.execute(pres_q)).scalars().all()
    for p in presentations:
        results.append({"type": "presentation", "id": p.id, "title": p.title, "snippet": "", "updated_at": p.updated_at})

    # Sort by updated_at descending
    results.sort(key=lambda x: x["updated_at"], reverse=True)
    return results[offset: offset + limit]


def _extract_snippet(html: str, query: str, max_len: int = 150) -> str:
    """Extract a text snippet around the query match."""
    import re
    text = re.sub(r"<[^>]+>", " ", html)
    text = " ".join(text.split())
    idx = text.lower().find(query.lower())
    if idx < 0:
        return text[:max_len] + "..." if len(text) > max_len else text
    start = max(0, idx - 50)
    end = min(len(text), idx + len(query) + 100)
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet
