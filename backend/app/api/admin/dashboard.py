from __future__ import annotations
"""Admin dashboard API."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import require_admin
from app.schemas.admin import DashboardStats
from app.services.admin_service import get_dashboard_stats

router = APIRouter(prefix="/admin/dashboard", tags=["admin"])


@router.get("", response_model=DashboardStats)
async def dashboard(user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await get_dashboard_stats(db)
