from __future__ import annotations
"""Template CRUD — create file from template, manage templates."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.template import Template
from app.utils.minio_client import upload_bytes, download_bytes


async def list_templates(db: AsyncSession, file_type: str | None = None, category: str | None = None, public_only: bool = True) -> list[Template]:
    q = select(Template)
    if file_type:
        q = q.where(Template.file_type == file_type)
    if category:
        q = q.where(Template.category == category)
    if public_only:
        q = q.where(Template.is_public == True)
    result = await db.execute(q.order_by(Template.name))
    return list(result.scalars().all())


async def get_template(db: AsyncSession, template_id: uuid.UUID) -> Template | None:
    result = await db.execute(select(Template).where(Template.id == template_id))
    return result.scalar_one_or_none()


async def create_template(db: AsyncSession, name: str, file_type: str, category: str, content_data: bytes, created_by: uuid.UUID | None = None, description: str | None = None, is_public: bool = False) -> Template:
    settings = get_settings()
    key = f"templates/{file_type}/{uuid.uuid4().hex}.bin"
    upload_bytes(settings.minio_bucket_snapshots, key, content_data)

    template = Template(
        name=name, file_type=file_type, category=category,
        content_snapshot_key=key, created_by=created_by,
        description=description, is_public=is_public,
    )
    db.add(template)
    await db.flush()
    return template


async def get_template_content(template: Template) -> bytes:
    settings = get_settings()
    return download_bytes(settings.minio_bucket_snapshots, template.content_snapshot_key)


async def delete_template(db: AsyncSession, template: Template) -> None:
    await db.delete(template)
    await db.flush()
