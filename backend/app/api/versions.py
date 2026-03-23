from __future__ import annotations
"""Version history API — list, get, restore, create manual snapshot."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.schemas.version import VersionCreate, VersionResponse
from app.schemas.common import MessageResponse
from app.services import version_service

router = APIRouter(prefix="/versions", tags=["versions"])


@router.get("/{file_type}/{file_id}", response_model=list[VersionResponse])
async def list_versions(file_type: str, file_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    versions = await version_service.list_versions(db, file_type, file_id)
    return [VersionResponse.model_validate(v) for v in versions]


@router.get("/detail/{version_id}", response_model=VersionResponse)
async def get_version(version_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    version = await version_service.get_version(db, version_id)
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return VersionResponse.model_validate(version)


@router.post("/{file_type}/{file_id}", response_model=VersionResponse, status_code=status.HTTP_201_CREATED)
async def create_manual_snapshot(file_type: str, file_id: uuid.UUID, body: VersionCreate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Get the file's current Yjs data
    if file_type == "document":
        from app.services.document_service import get_document
        file_obj = await get_document(db, file_id)
        if not file_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        yjs_data = file_obj.content_yjs or b""
        title = file_obj.title
    elif file_type == "spreadsheet":
        from app.services.spreadsheet_service import get_spreadsheet
        file_obj = await get_spreadsheet(db, file_id)
        if not file_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spreadsheet not found")
        yjs_data = file_obj.sheets_yjs or b""
        title = file_obj.title
    elif file_type == "presentation":
        from app.services.presentation_service import get_presentation
        file_obj = await get_presentation(db, file_id)
        if not file_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presentation not found")
        yjs_data = file_obj.slides_yjs or b""
        title = file_obj.title
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")

    version = await version_service.create_snapshot(db, file_type, file_id, title, yjs_data, user.id, body.name)
    return VersionResponse.model_validate(version)


@router.post("/restore/{version_id}", response_model=MessageResponse)
async def restore_version(version_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    version = await version_service.get_version(db, version_id)
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

    yjs_data = await version_service.get_version_data(version)

    if version.file_type == "document":
        from app.services.document_service import get_document, update_document_content
        doc = await get_document(db, version.file_id)
        if doc:
            await update_document_content(db, doc, content_yjs=yjs_data, editor_id=user.id)
    elif version.file_type == "spreadsheet":
        from app.services.spreadsheet_service import get_spreadsheet, update_spreadsheet_content
        sheet = await get_spreadsheet(db, version.file_id)
        if sheet:
            await update_spreadsheet_content(db, sheet, sheets_yjs=yjs_data, editor_id=user.id)
    elif version.file_type == "presentation":
        from app.services.presentation_service import get_presentation, update_presentation_content
        pres = await get_presentation(db, version.file_id)
        if pres:
            await update_presentation_content(db, pres, slides_yjs=yjs_data, editor_id=user.id)

    return MessageResponse(message=f"Restored to version {version.version_number}")
