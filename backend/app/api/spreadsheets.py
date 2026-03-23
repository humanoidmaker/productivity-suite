from __future__ import annotations
"""Spreadsheet API — CRUD, import, export."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.schemas.spreadsheet import SpreadsheetCreate, SpreadsheetUpdate, SpreadsheetResponse
from app.services import spreadsheet_service
from app.services.activity_service import log_activity
from app.utils.pagination import PaginationParams, PaginatedResponse, get_pagination

router = APIRouter(prefix="/spreadsheets", tags=["spreadsheets"])


@router.post("", response_model=SpreadsheetResponse, status_code=status.HTTP_201_CREATED)
async def create_spreadsheet(body: SpreadsheetCreate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sheet = await spreadsheet_service.create_spreadsheet(db, user.id, body.title, body.folder_id)
    await log_activity(db, user.id, "spreadsheet.create", "spreadsheet", sheet.id)
    return SpreadsheetResponse.model_validate(sheet)


@router.get("", response_model=PaginatedResponse)
async def list_spreadsheets(folder_id: uuid.UUID | None = None, pagination: PaginationParams = Depends(get_pagination), user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    items, total = await spreadsheet_service.list_spreadsheets(db, user.id, folder_id, pagination.offset, pagination.limit)
    return PaginatedResponse.create([SpreadsheetResponse.model_validate(s) for s in items], total, pagination)


@router.get("/{sheet_id}", response_model=SpreadsheetResponse)
async def get_spreadsheet(sheet_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sheet = await spreadsheet_service.get_spreadsheet(db, sheet_id)
    if not sheet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spreadsheet not found")
    return SpreadsheetResponse.model_validate(sheet)


@router.patch("/{sheet_id}", response_model=SpreadsheetResponse)
async def update_spreadsheet(sheet_id: uuid.UUID, body: SpreadsheetUpdate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sheet = await spreadsheet_service.get_spreadsheet(db, sheet_id)
    if not sheet or sheet.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spreadsheet not found")
    updated = await spreadsheet_service.update_spreadsheet_meta(db, sheet, body.title, body.folder_id, body.sheets_meta_json)
    return SpreadsheetResponse.model_validate(updated)


@router.post("/{sheet_id}/duplicate", response_model=SpreadsheetResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_spreadsheet(sheet_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sheet = await spreadsheet_service.get_spreadsheet(db, sheet_id)
    if not sheet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spreadsheet not found")
    new_sheet = await spreadsheet_service.duplicate_spreadsheet(db, sheet, user.id)
    return SpreadsheetResponse.model_validate(new_sheet)


@router.delete("/{sheet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spreadsheet(sheet_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sheet = await spreadsheet_service.get_spreadsheet(db, sheet_id)
    if not sheet or sheet.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spreadsheet not found")
    await spreadsheet_service.soft_delete_spreadsheet(db, sheet)


@router.post("/{sheet_id}/export/{format}")
async def export_spreadsheet(sheet_id: uuid.UUID, format: str, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sheet = await spreadsheet_service.get_spreadsheet(db, sheet_id)
    if not sheet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spreadsheet not found")

    if format == "xlsx":
        from app.export.xlsx_exporter import export_spreadsheet as do_export
        data = do_export(sheet.sheets_meta_json or {}, sheet.title)
        return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       headers={"Content-Disposition": f'attachment; filename="{sheet.title}.xlsx"'})
    elif format == "csv":
        from app.export.csv_exporter import export_csv
        data = export_csv(sheet.sheets_meta_json or {})
        return Response(content=data.encode(), media_type="text/csv",
                       headers={"Content-Disposition": f'attachment; filename="{sheet.title}.csv"'})

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported format: {format}")


@router.post("/import", response_model=SpreadsheetResponse, status_code=status.HTTP_201_CREATED)
async def import_spreadsheet(file: UploadFile = File(...), user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    data = await file.read()
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if ext == "xlsx":
        from app.importer.xlsx_importer import import_xlsx
        meta = import_xlsx(data)
    elif ext == "csv":
        from app.importer.csv_importer import import_csv
        meta = import_csv(data)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported: .{ext}")

    title = file.filename.rsplit(".", 1)[0] if "." in file.filename else file.filename
    sheet = await spreadsheet_service.create_spreadsheet(db, user.id, title)
    await spreadsheet_service.update_spreadsheet_meta(db, sheet, sheets_meta=meta)
    await log_activity(db, user.id, "spreadsheet.import", "spreadsheet", sheet.id)
    return SpreadsheetResponse.model_validate(sheet)
