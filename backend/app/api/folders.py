from __future__ import annotations
"""Folder API — CRUD, move, list contents, breadcrumbs, tree."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.schemas.folder import FolderCreate, FolderUpdate, FolderMove, FolderResponse, BreadcrumbItem
from app.services import folder_service

router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(body: FolderCreate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    folder = await folder_service.create_folder(db, user.id, body.name, body.parent_folder_id, body.color, body.icon)
    return FolderResponse.model_validate(folder)


@router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(folder_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    folder = await folder_service.get_folder(db, folder_id)
    if not folder or folder.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    return FolderResponse.model_validate(folder)


@router.patch("/{folder_id}", response_model=FolderResponse)
async def update_folder(folder_id: uuid.UUID, body: FolderUpdate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    folder = await folder_service.get_folder(db, folder_id)
    if not folder or folder.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    updated = await folder_service.update_folder(db, folder, body.name, body.color, body.icon)
    return FolderResponse.model_validate(updated)


@router.post("/{folder_id}/move", response_model=FolderResponse)
async def move_folder(folder_id: uuid.UUID, body: FolderMove, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    folder = await folder_service.get_folder(db, folder_id)
    if not folder or folder.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    moved = await folder_service.move_folder(db, folder, body.parent_folder_id)
    return FolderResponse.model_validate(moved)


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(folder_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    folder = await folder_service.get_folder(db, folder_id)
    if not folder or folder.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    await folder_service.soft_delete_folder(db, folder)


@router.get("/{folder_id}/contents")
async def list_contents(folder_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await folder_service.list_folder_contents(db, user.id, folder_id)


@router.get("", tags=["folders"])
async def list_root_contents(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await folder_service.list_folder_contents(db, user.id, None)


@router.get("/{folder_id}/breadcrumb", response_model=list[BreadcrumbItem])
async def get_breadcrumb(folder_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await folder_service.get_breadcrumb(db, folder_id)


@router.get("/tree/all")
async def get_folder_tree(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await folder_service.get_folder_tree(db, user.id)
