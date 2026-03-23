from __future__ import annotations
"""Spreadsheet CRUD and sheet management."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.spreadsheet import Spreadsheet


DEFAULT_SHEETS_META = {
    "sheets": [{"name": "Sheet1", "index": 0, "visible": True, "color": None}],
}


async def create_spreadsheet(db: AsyncSession, owner_id: uuid.UUID, title: str = "Untitled Spreadsheet", folder_id: uuid.UUID | None = None) -> Spreadsheet:
    sheet = Spreadsheet(title=title, owner_id=owner_id, folder_id=folder_id, sheets_meta_json=DEFAULT_SHEETS_META)
    db.add(sheet)
    await db.flush()
    return sheet


async def get_spreadsheet(db: AsyncSession, sheet_id: uuid.UUID) -> Spreadsheet | None:
    result = await db.execute(select(Spreadsheet).where(Spreadsheet.id == sheet_id))
    return result.scalar_one_or_none()


async def list_spreadsheets(db: AsyncSession, owner_id: uuid.UUID, folder_id: uuid.UUID | None = None, offset: int = 0, limit: int = 20) -> tuple[list[Spreadsheet], int]:
    base = select(Spreadsheet).where(Spreadsheet.owner_id == owner_id, Spreadsheet.is_trashed == False)
    if folder_id is not None:
        base = base.where(Spreadsheet.folder_id == folder_id)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    items = (await db.execute(base.order_by(Spreadsheet.updated_at.desc()).offset(offset).limit(limit))).scalars().all()
    return list(items), total


async def update_spreadsheet_meta(db: AsyncSession, sheet: Spreadsheet, title: str | None = None, folder_id: uuid.UUID | None = ..., sheets_meta: dict | None = None) -> Spreadsheet:
    if title is not None:
        sheet.title = title
    if folder_id is not ...:
        sheet.folder_id = folder_id
    if sheets_meta is not None:
        sheet.sheets_meta_json = sheets_meta
    sheet.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return sheet


async def update_spreadsheet_content(db: AsyncSession, sheet: Spreadsheet, sheets_yjs: bytes | None = None, editor_id: uuid.UUID | None = None) -> Spreadsheet:
    if sheets_yjs is not None:
        sheet.sheets_yjs = sheets_yjs
    if editor_id:
        sheet.last_edited_by = editor_id
    sheet.last_edited_at = datetime.now(timezone.utc)
    await db.flush()
    return sheet


async def duplicate_spreadsheet(db: AsyncSession, sheet: Spreadsheet, new_owner_id: uuid.UUID | None = None) -> Spreadsheet:
    new_sheet = Spreadsheet(
        title=f"{sheet.title} (Copy)",
        owner_id=new_owner_id or sheet.owner_id,
        folder_id=sheet.folder_id,
        sheets_yjs=sheet.sheets_yjs,
        sheets_meta_json=sheet.sheets_meta_json,
        row_count=sheet.row_count,
        col_count=sheet.col_count,
    )
    db.add(new_sheet)
    await db.flush()
    return new_sheet


async def soft_delete_spreadsheet(db: AsyncSession, sheet: Spreadsheet) -> None:
    sheet.is_trashed = True
    sheet.trashed_at = datetime.now(timezone.utc)
    await db.flush()


async def restore_spreadsheet(db: AsyncSession, sheet: Spreadsheet) -> None:
    sheet.is_trashed = False
    sheet.trashed_at = None
    await db.flush()


async def permanent_delete_spreadsheet(db: AsyncSession, sheet: Spreadsheet) -> None:
    await db.delete(sheet)
    await db.flush()
