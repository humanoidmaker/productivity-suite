from __future__ import annotations
"""Admin user management API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import require_admin
from app.models.user import User
from app.schemas.user import UserResponse, AdminCreateUserRequest, AdminUpdateUserRequest
from app.utils.hashing import hash_password
from app.utils.pagination import PaginationParams, PaginatedResponse, get_pagination
from app.services.admin_service import list_all_users

router = APIRouter(prefix="/admin/users", tags=["admin"])


@router.get("", response_model=PaginatedResponse)
async def list_users(search: str | None = None, pagination: PaginationParams = Depends(get_pagination), user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    users, total = await list_all_users(db, pagination.offset, pagination.limit, search)
    return PaginatedResponse.create([UserResponse.model_validate(u) for u in users], total, pagination)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(body: AdminCreateUserRequest, user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email exists")
    new_user = User(email=body.email.lower(), name=body.name, password_hash=hash_password(body.password), role=body.role, storage_quota=body.storage_quota)
    db.add(new_user)
    await db.flush()
    return UserResponse.model_validate(new_user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: uuid.UUID, body: AdminUpdateUserRequest, user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if body.name is not None:
        target.name = body.name
    if body.role is not None:
        target.role = body.role
    if body.is_active is not None:
        target.is_active = body.is_active
    if body.storage_quota is not None:
        target.storage_quota = body.storage_quota
    await db.flush()
    return UserResponse.model_validate(target)


@router.post("/{user_id}/reset-password")
async def reset_password(user_id: uuid.UUID, new_password: str = Query(..., min_length=8), user=Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    target.password_hash = hash_password(new_password)
    await db.flush()
    return {"message": "Password reset"}
