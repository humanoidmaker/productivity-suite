from __future__ import annotations
"""Sharing API — share with users, link sharing, permission management."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user, get_optional_user
from app.schemas.share import ShareCreate, ShareLinkCreate, ShareUpdate, ShareResponse
from app.services import share_service

router = APIRouter(prefix="/shares", tags=["sharing"])


@router.post("", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
async def share_with_user(body: ShareCreate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not body.shared_with_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email required")
    share = await share_service.share_with_user(db, body.file_type, body.file_id, user.id, body.shared_with_email, body.permission)
    return ShareResponse.model_validate(share)


@router.post("/link", response_model=ShareResponse, status_code=status.HTTP_201_CREATED)
async def create_share_link(body: ShareLinkCreate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    share = await share_service.create_share_link(db, body.file_type, body.file_id, user.id, body.permission, body.password, body.expires_at)
    return ShareResponse.model_validate(share)


@router.get("/file/{file_type}/{file_id}", response_model=list[ShareResponse])
async def list_shares(file_type: str, file_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    shares = await share_service.list_shares_for_file(db, file_type, file_id)
    return [ShareResponse.model_validate(s) for s in shares]


@router.get("/shared-with-me", response_model=list[ShareResponse])
async def shared_with_me(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    shares = await share_service.list_shared_with_user(db, user.id)
    return [ShareResponse.model_validate(s) for s in shares]


@router.get("/token/{token}")
async def access_shared_link(token: str, password: str | None = None, db: AsyncSession = Depends(get_db)):
    share = await share_service.get_share_by_token(db, token)
    if not share:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share link not found or expired")
    if share.password_hash and not password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password required")
    if share.password_hash and password:
        if not await share_service.verify_share_password(share, password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    return ShareResponse.model_validate(share)


@router.patch("/{share_id}", response_model=ShareResponse)
async def update_share(share_id: uuid.UUID, body: ShareUpdate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.share import Share
    result = await db.execute(select(Share).where(Share.id == share_id))
    share = result.scalar_one_or_none()
    if not share or share.shared_by != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    updated = await share_service.update_share_permission(db, share, body.permission)
    return ShareResponse.model_validate(updated)


@router.delete("/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_share(share_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.share import Share
    result = await db.execute(select(Share).where(Share.id == share_id))
    share = result.scalar_one_or_none()
    if not share or share.shared_by != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    await share_service.revoke_share(db, share)
