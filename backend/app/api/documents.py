from __future__ import annotations
"""Document API — CRUD, import, export, content."""

import base64
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse, DocumentContentResponse
from app.services import document_service
from app.services.activity_service import log_activity
from app.utils.pagination import PaginationParams, PaginatedResponse, get_pagination

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(body: DocumentCreate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc = await document_service.create_document(db, user.id, body.title, body.folder_id)
    await log_activity(db, user.id, "document.create", "document", doc.id)
    return DocumentResponse.model_validate(doc)


@router.get("", response_model=PaginatedResponse)
async def list_documents(folder_id: uuid.UUID | None = None, pagination: PaginationParams = Depends(get_pagination), user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    items, total = await document_service.list_documents(db, user.id, folder_id, pagination.offset, pagination.limit)
    return PaginatedResponse.create([DocumentResponse.model_validate(d) for d in items], total, pagination)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc = await document_service.get_document(db, doc_id)
    if not doc or (doc.owner_id != user.id and doc.is_trashed):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(doc)


@router.get("/{doc_id}/content", response_model=DocumentContentResponse)
async def get_document_content(doc_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc = await document_service.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    yjs_b64 = base64.b64encode(doc.content_yjs).decode() if doc.content_yjs else None
    return DocumentContentResponse(id=doc.id, title=doc.title, content_html=doc.content_html, content_yjs_base64=yjs_b64, page_settings_json=doc.page_settings_json)


@router.patch("/{doc_id}", response_model=DocumentResponse)
async def update_document(doc_id: uuid.UUID, body: DocumentUpdate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if body.content_html is not None:
        await document_service.update_document_content(db, doc, content_html=body.content_html, editor_id=user.id)
    updated = await document_service.update_document_meta(db, doc, body.title, body.folder_id, body.page_settings_json)
    return DocumentResponse.model_validate(updated)


@router.post("/{doc_id}/duplicate", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_document(doc_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc = await document_service.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    new_doc = await document_service.duplicate_document(db, doc, user.id)
    return DocumentResponse.model_validate(new_doc)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(doc_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc = await document_service.get_document(db, doc_id)
    if not doc or doc.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    await document_service.soft_delete_document(db, doc)
    await log_activity(db, user.id, "document.delete", "document", doc.id)


@router.post("/{doc_id}/export/{format}")
async def export_document(doc_id: uuid.UUID, format: str, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc = await document_service.get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if format not in ("docx", "pdf", "html", "md", "txt"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported format: {format}")

    # Dispatch to export engine (Celery task for large files, inline for small)
    from app.export import docx_exporter, pdf_exporter, html_exporter
    from fastapi.responses import Response

    if format == "docx":
        data = docx_exporter.export_document(doc.content_html or "", doc.title)
        return Response(content=data, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                       headers={"Content-Disposition": f'attachment; filename="{doc.title}.docx"'})
    elif format == "pdf":
        data = pdf_exporter.export_html_to_pdf(doc.content_html or "", doc.title)
        return Response(content=data, media_type="application/pdf",
                       headers={"Content-Disposition": f'attachment; filename="{doc.title}.pdf"'})
    elif format == "html":
        data = html_exporter.export_standalone_html(doc.content_html or "", doc.title)
        return Response(content=data.encode(), media_type="text/html",
                       headers={"Content-Disposition": f'attachment; filename="{doc.title}.html"'})
    elif format == "txt":
        import re
        text = re.sub(r"<[^>]+>", " ", doc.content_html or "")
        text = " ".join(text.split())
        return Response(content=text.encode(), media_type="text/plain",
                       headers={"Content-Disposition": f'attachment; filename="{doc.title}.txt"'})

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported format")


@router.post("/import", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def import_document(file: UploadFile = File(...), user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    data = await file.read()
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if ext == "docx":
        from app.importer.docx_importer import import_docx
        html = import_docx(data)
    elif ext in ("html", "htm"):
        html = data.decode("utf-8", errors="replace")
    elif ext == "txt":
        text = data.decode("utf-8", errors="replace")
        html = f"<p>{text}</p>"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type: .{ext}")

    title = file.filename.rsplit(".", 1)[0] if "." in file.filename else file.filename
    doc = await document_service.create_document(db, user.id, title)
    await document_service.update_document_content(db, doc, content_html=html, editor_id=user.id)
    await log_activity(db, user.id, "document.import", "document", doc.id, details={"filename": file.filename})
    return DocumentResponse.model_validate(doc)
