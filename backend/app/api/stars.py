from __future__ import annotations
"""Stars API — star/unstar files, list starred."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.models.star import Star

router = APIRouter(prefix="/stars", tags=["stars"])


@router.post("/{file_type}/{file_id}", status_code=status.HTTP_201_CREATED)
async def star_file(file_type: str, file_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Star).where(Star.user_id == user.id, Star.file_type == file_type, Star.file_id == file_id))
    if existing.scalar_one_or_none():
        return {"message": "Already starred"}
    star = Star(user_id=user.id, file_type=file_type, file_id=file_id)
    db.add(star)
    await db.flush()
    return {"message": "Starred"}


@router.delete("/{file_type}/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unstar_file(file_type: str, file_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Star).where(Star.user_id == user.id, Star.file_type == file_type, Star.file_id == file_id))
    await db.flush()


@router.get("", response_model=list[dict])
async def list_starred(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Star).where(Star.user_id == user.id).order_by(Star.created_at.desc()))
    stars = result.scalars().all()
    return [{"file_type": s.file_type, "file_id": s.file_id, "created_at": s.created_at} for s in stars]
