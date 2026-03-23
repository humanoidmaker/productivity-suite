from __future__ import annotations
"""Admin aggregations and system health."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.document import Document
from app.models.spreadsheet import Spreadsheet
from app.models.presentation import Presentation


async def get_dashboard_stats(db: AsyncSession) -> dict:
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    active_users = (await db.execute(select(func.count(User.id)).where(User.is_active == True))).scalar() or 0
    total_docs = (await db.execute(select(func.count(Document.id)).where(Document.is_trashed == False))).scalar() or 0
    total_sheets = (await db.execute(select(func.count(Spreadsheet.id)).where(Spreadsheet.is_trashed == False))).scalar() or 0
    total_pres = (await db.execute(select(func.count(Presentation.id)).where(Presentation.is_trashed == False))).scalar() or 0
    total_storage = (await db.execute(select(func.coalesce(func.sum(User.storage_used), 0)))).scalar() or 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_documents": total_docs,
        "total_spreadsheets": total_sheets,
        "total_presentations": total_pres,
        "total_storage_bytes": total_storage,
        "active_collaborations": 0,  # Will be populated from WebSocket manager
    }


async def list_all_users(db: AsyncSession, offset: int = 0, limit: int = 50, search: str | None = None) -> tuple[list[User], int]:
    q = select(User)
    if search:
        q = q.where(User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
    users = (await db.execute(q.order_by(User.created_at.desc()).offset(offset).limit(limit))).scalars().all()
    return list(users), total
