from __future__ import annotations
"""Image/file upload to MinIO, asset management."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.asset import Asset
from app.utils.file_utils import generate_storage_key, sanitize_filename
from app.utils.minio_client import upload_bytes, get_presigned_url, delete_object


async def upload_asset(db: AsyncSession, owner_id: uuid.UUID, file_name: str, mime_type: str, data: bytes) -> Asset:
    settings = get_settings()
    safe_name = sanitize_filename(file_name)
    key = generate_storage_key("assets", safe_name)
    upload_bytes(settings.minio_bucket_assets, key, data, content_type=mime_type)

    asset = Asset(
        owner_id=owner_id,
        file_name=safe_name,
        mime_type=mime_type,
        size=len(data),
        storage_key=key,
    )
    db.add(asset)
    await db.flush()
    return asset


async def list_user_assets(db: AsyncSession, owner_id: uuid.UUID, offset: int = 0, limit: int = 50) -> list[Asset]:
    result = await db.execute(
        select(Asset).where(Asset.owner_id == owner_id).order_by(Asset.created_at.desc()).offset(offset).limit(limit)
    )
    return list(result.scalars().all())


async def get_asset(db: AsyncSession, asset_id: uuid.UUID) -> Asset | None:
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    return result.scalar_one_or_none()


async def get_asset_url(asset: Asset) -> str:
    settings = get_settings()
    return get_presigned_url(settings.minio_bucket_assets, asset.storage_key)


async def delete_asset(db: AsyncSession, asset: Asset) -> None:
    settings = get_settings()
    try:
        delete_object(settings.minio_bucket_assets, asset.storage_key)
    except Exception:
        pass  # Object may already be deleted
    await db.delete(asset)
    await db.flush()
