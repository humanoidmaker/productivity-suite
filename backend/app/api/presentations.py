from __future__ import annotations
"""Presentation API — CRUD, import, export."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.schemas.presentation import PresentationCreate, PresentationUpdate, PresentationResponse
from app.services import presentation_service
from app.services.activity_service import log_activity
from app.utils.pagination import PaginationParams, PaginatedResponse, get_pagination

router = APIRouter(prefix="/presentations", tags=["presentations"])


@router.post("", response_model=PresentationResponse, status_code=status.HTTP_201_CREATED)
async def create_presentation(body: PresentationCreate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pres = await presentation_service.create_presentation(db, user.id, body.title, body.folder_id, body.aspect_ratio)
    await log_activity(db, user.id, "presentation.create", "presentation", pres.id)
    return PresentationResponse.model_validate(pres)


@router.get("", response_model=PaginatedResponse)
async def list_presentations(folder_id: uuid.UUID | None = None, pagination: PaginationParams = Depends(get_pagination), user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    items, total = await presentation_service.list_presentations(db, user.id, folder_id, pagination.offset, pagination.limit)
    return PaginatedResponse.create([PresentationResponse.model_validate(p) for p in items], total, pagination)


@router.get("/{pres_id}", response_model=PresentationResponse)
async def get_presentation(pres_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pres = await presentation_service.get_presentation(db, pres_id)
    if not pres:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presentation not found")
    return PresentationResponse.model_validate(pres)


@router.patch("/{pres_id}", response_model=PresentationResponse)
async def update_presentation(pres_id: uuid.UUID, body: PresentationUpdate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pres = await presentation_service.get_presentation(db, pres_id)
    if not pres or pres.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presentation not found")
    updated = await presentation_service.update_presentation_meta(db, pres, body.title, body.folder_id, body.slides_meta_json, body.theme_json, body.aspect_ratio)
    return PresentationResponse.model_validate(updated)


@router.post("/{pres_id}/duplicate", response_model=PresentationResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_presentation(pres_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pres = await presentation_service.get_presentation(db, pres_id)
    if not pres:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presentation not found")
    new_pres = await presentation_service.duplicate_presentation(db, pres, user.id)
    return PresentationResponse.model_validate(new_pres)


@router.delete("/{pres_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_presentation(pres_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pres = await presentation_service.get_presentation(db, pres_id)
    if not pres or pres.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presentation not found")
    await presentation_service.soft_delete_presentation(db, pres)


@router.post("/{pres_id}/export/{format}")
async def export_presentation(pres_id: uuid.UUID, format: str, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pres = await presentation_service.get_presentation(db, pres_id)
    if not pres:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Presentation not found")

    if format == "pptx":
        from app.export.pptx_exporter import export_presentation as do_export
        data = do_export(pres.slides_meta_json or {}, pres.theme_json or {}, pres.title)
        return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                       headers={"Content-Disposition": f'attachment; filename="{pres.title}.pptx"'})

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported format: {format}")


@router.post("/import", response_model=PresentationResponse, status_code=status.HTTP_201_CREATED)
async def import_presentation(file: UploadFile = File(...), user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    data = await file.read()
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if ext != "pptx":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported: .{ext}")

    from app.importer.pptx_importer import import_pptx
    meta, theme = import_pptx(data)

    title = file.filename.rsplit(".", 1)[0] if "." in file.filename else file.filename
    pres = await presentation_service.create_presentation(db, user.id, title)
    await presentation_service.update_presentation_meta(db, pres, slides_meta=meta, theme=theme)
    await log_activity(db, user.id, "presentation.import", "presentation", pres.id)
    return PresentationResponse.model_validate(pres)
