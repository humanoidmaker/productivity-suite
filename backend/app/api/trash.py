from __future__ import annotations
"""Trash API — list, restore, permanent delete, empty."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.schemas.common import MessageResponse
from app.services import trash_service

router = APIRouter(prefix="/trash", tags=["trash"])


@router.get("")
async def list_trash(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await trash_service.list_trash(db, user.id)


@router.post("/restore/{file_type}/{file_id}", response_model=MessageResponse)
async def restore_item(file_type: str, file_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await trash_service.restore_item(db, file_type, file_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in trash")
    return MessageResponse(message="Restored")


@router.delete("/{file_type}/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def permanent_delete(file_type: str, file_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    success = await trash_service.permanent_delete_item(db, file_type, file_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in trash")


@router.delete("", response_model=MessageResponse)
async def empty_trash(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    count = await trash_service.empty_trash(db, user.id)
    return MessageResponse(message=f"Deleted {count} items permanently")
