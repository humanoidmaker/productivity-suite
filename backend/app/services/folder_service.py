from __future__ import annotations
"""Folder CRUD, tree operations, recursive actions."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.folder import Folder
from app.models.document import Document
from app.models.spreadsheet import Spreadsheet
from app.models.presentation import Presentation


async def create_folder(db: AsyncSession, owner_id: uuid.UUID, name: str, parent_id: uuid.UUID | None = None, color: str | None = None, icon: str | None = None) -> Folder:
    folder = Folder(name=name, owner_id=owner_id, parent_folder_id=parent_id, color=color, icon=icon)
    db.add(folder)
    await db.flush()
    return folder


async def get_folder(db: AsyncSession, folder_id: uuid.UUID) -> Folder | None:
    result = await db.execute(select(Folder).where(Folder.id == folder_id, Folder.is_trashed == False))
    return result.scalar_one_or_none()


async def update_folder(db: AsyncSession, folder: Folder, name: str | None = None, color: str | None = None, icon: str | None = None) -> Folder:
    if name is not None:
        folder.name = name
    if color is not None:
        folder.color = color
    if icon is not None:
        folder.icon = icon
    await db.flush()
    return folder


async def move_folder(db: AsyncSession, folder: Folder, new_parent_id: uuid.UUID | None) -> Folder:
    folder.parent_folder_id = new_parent_id
    await db.flush()
    return folder


async def soft_delete_folder(db: AsyncSession, folder: Folder) -> None:
    now = datetime.now(timezone.utc)
    folder.is_trashed = True
    folder.trashed_at = now
    await db.flush()


async def restore_folder(db: AsyncSession, folder: Folder) -> None:
    folder.is_trashed = False
    folder.trashed_at = None
    await db.flush()


async def list_folder_contents(db: AsyncSession, owner_id: uuid.UUID, folder_id: uuid.UUID | None = None):
    """List folders, documents, spreadsheets, presentations in a folder."""
    folder_q = select(Folder).where(Folder.owner_id == owner_id, Folder.parent_folder_id == folder_id, Folder.is_trashed == False)
    folders = (await db.execute(folder_q)).scalars().all()

    doc_q = select(Document).where(Document.owner_id == owner_id, Document.folder_id == folder_id, Document.is_trashed == False)
    docs = (await db.execute(doc_q)).scalars().all()

    sheet_q = select(Spreadsheet).where(Spreadsheet.owner_id == owner_id, Spreadsheet.folder_id == folder_id, Spreadsheet.is_trashed == False)
    sheets = (await db.execute(sheet_q)).scalars().all()

    pres_q = select(Presentation).where(Presentation.owner_id == owner_id, Presentation.folder_id == folder_id, Presentation.is_trashed == False)
    presentations = (await db.execute(pres_q)).scalars().all()

    return {"folders": list(folders), "documents": list(docs), "spreadsheets": list(sheets), "presentations": list(presentations)}


async def get_breadcrumb(db: AsyncSession, folder_id: uuid.UUID) -> list[dict]:
    """Get breadcrumb path from root to folder."""
    path = []
    current_id = folder_id
    while current_id:
        result = await db.execute(select(Folder).where(Folder.id == current_id))
        folder = result.scalar_one_or_none()
        if not folder:
            break
        path.append({"id": folder.id, "name": folder.name})
        current_id = folder.parent_folder_id
    path.reverse()
    return path


async def get_folder_tree(db: AsyncSession, owner_id: uuid.UUID) -> list[dict]:
    """Get flat list of all folders for tree rendering."""
    result = await db.execute(select(Folder).where(Folder.owner_id == owner_id, Folder.is_trashed == False).order_by(Folder.name))
    folders = result.scalars().all()
    return [{"id": f.id, "name": f.name, "parent_folder_id": f.parent_folder_id, "color": f.color, "icon": f.icon} for f in folders]
