from __future__ import annotations
"""Asset API — upload images/files, list, delete, get URL."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.schemas.asset import AssetResponse
from app.services import asset_service, quota_service
from app.utils.file_utils import is_valid_image_type, validate_file_size
from app.config import get_settings

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset(file: UploadFile = File(...), user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    data = await file.read()

    if not validate_file_size(len(data), settings.max_file_size_mb):
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"File too large (max {settings.max_file_size_mb}MB)")

    if not await quota_service.check_quota(db, user.id, len(data)):
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Storage quota exceeded")

    asset = await asset_service.upload_asset(db, user.id, file.filename, file.content_type or "application/octet-stream", data)
    await quota_service.refresh_storage_used(db, user.id)
    url = await asset_service.get_asset_url(asset)
    resp = AssetResponse.model_validate(asset)
    resp.url = url
    return resp


@router.get("", response_model=list[AssetResponse])
async def list_assets(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    assets = await asset_service.list_user_assets(db, user.id)
    results = []
    for a in assets:
        resp = AssetResponse.model_validate(a)
        resp.url = await asset_service.get_asset_url(a)
        results.append(resp)
    return results


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    asset = await asset_service.get_asset(db, asset_id)
    if not asset or asset.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    await asset_service.delete_asset(db, asset)
    await quota_service.refresh_storage_used(db, user.id)
