from __future__ import annotations
"""Search API — full-text search across all file types."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.services import search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def search(q: str = Query(..., min_length=1), offset: int = 0, limit: int = 20, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    results = await search_service.search_files(db, user.id, q, offset, limit)
    return {"query": q, "results": results, "count": len(results)}
