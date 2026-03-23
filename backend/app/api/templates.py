from __future__ import annotations
"""Templates API — list, get, create from file, use template."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.schemas.template import TemplateResponse
from app.schemas.common import IdResponse
from app.services import template_service, document_service, spreadsheet_service, presentation_service

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TemplateResponse])
async def list_templates(file_type: str | None = None, category: str | None = None, db: AsyncSession = Depends(get_db)):
    templates = await template_service.list_templates(db, file_type, category)
    return [TemplateResponse.model_validate(t) for t in templates]


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    template = await template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return TemplateResponse.model_validate(template)


@router.post("/{template_id}/use", response_model=IdResponse, status_code=status.HTTP_201_CREATED)
async def use_template(template_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create a new file from a template."""
    template = await template_service.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    content = await template_service.get_template_content(template)

    if template.file_type == "document":
        doc = await document_service.create_document(db, user.id, template.name)
        await document_service.update_document_content(db, doc, content_yjs=content, editor_id=user.id)
        return IdResponse(id=doc.id)
    elif template.file_type == "spreadsheet":
        sheet = await spreadsheet_service.create_spreadsheet(db, user.id, template.name)
        await spreadsheet_service.update_spreadsheet_content(db, sheet, sheets_yjs=content, editor_id=user.id)
        return IdResponse(id=sheet.id)
    elif template.file_type == "presentation":
        pres = await presentation_service.create_presentation(db, user.id, template.name)
        await presentation_service.update_presentation_content(db, pres, slides_yjs=content, editor_id=user.id)
        return IdResponse(id=pres.id)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid template type")
