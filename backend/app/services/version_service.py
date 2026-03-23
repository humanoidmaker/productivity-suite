from __future__ import annotations
"""Version snapshots — auto/manual snapshot, restore, list."""

import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.file_version import FileVersion
from app.utils.minio_client import upload_bytes, download_bytes


async def create_snapshot(db: AsyncSession, file_type: str, file_id: uuid.UUID, title: str, yjs_data: bytes, created_by: uuid.UUID | None = None, name: str | None = None) -> FileVersion:
    settings = get_settings()

    # Get next version number
    result = await db.execute(
        select(func.coalesce(func.max(FileVersion.version_number), 0))
        .where(FileVersion.file_type == file_type, FileVersion.file_id == file_id)
    )
    next_version = (result.scalar() or 0) + 1

    # Upload snapshot to MinIO
    key = f"versions/{file_type}/{file_id}/{next_version}.yjs"
    upload_bytes(settings.minio_bucket_snapshots, key, yjs_data)

    version = FileVersion(
        file_type=file_type, file_id=file_id,
        version_number=next_version, snapshot_key=key,
        title_at_version=title, name=name, created_by=created_by,
    )
    db.add(version)
    await db.flush()

    # Trim old versions
    await _trim_versions(db, file_type, file_id, settings.max_versions_per_file)

    return version


async def list_versions(db: AsyncSession, file_type: str, file_id: uuid.UUID) -> list[FileVersion]:
    result = await db.execute(
        select(FileVersion)
        .where(FileVersion.file_type == file_type, FileVersion.file_id == file_id)
        .order_by(FileVersion.version_number.desc())
    )
    return list(result.scalars().all())


async def get_version(db: AsyncSession, version_id: uuid.UUID) -> FileVersion | None:
    result = await db.execute(select(FileVersion).where(FileVersion.id == version_id))
    return result.scalar_one_or_none()


async def get_version_data(version: FileVersion) -> bytes:
    settings = get_settings()
    return download_bytes(settings.minio_bucket_snapshots, version.snapshot_key)


async def _trim_versions(db: AsyncSession, file_type: str, file_id: uuid.UUID, max_count: int) -> None:
    """Delete oldest versions beyond max_count."""
    result = await db.execute(
        select(FileVersion)
        .where(FileVersion.file_type == file_type, FileVersion.file_id == file_id)
        .order_by(FileVersion.version_number.desc())
        .offset(max_count)
    )
    old_versions = result.scalars().all()
    for v in old_versions:
        await db.delete(v)
    await db.flush()
