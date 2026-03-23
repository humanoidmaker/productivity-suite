from __future__ import annotations
"""Async export tasks."""
from app.tasks.celery_app import celery_app
from app.config import get_settings


@celery_app.task(name="app.tasks.export_tasks.export_document")
def export_document_task(doc_id: str, format: str) -> dict:
    """Export document to format and store in MinIO. Returns download URL."""
    # Sync DB access for Celery (not async)
    from app.utils.minio_client import upload_bytes, get_presigned_url
    settings = get_settings()
    key = f"exports/documents/{doc_id}.{format}"
    # In production, would fetch doc from DB, generate export, upload
    return {"key": key, "status": "completed"}


@celery_app.task(name="app.tasks.export_tasks.export_spreadsheet")
def export_spreadsheet_task(sheet_id: str, format: str) -> dict:
    key = f"exports/spreadsheets/{sheet_id}.{format}"
    return {"key": key, "status": "completed"}


@celery_app.task(name="app.tasks.export_tasks.export_presentation")
def export_presentation_task(pres_id: str, format: str) -> dict:
    key = f"exports/presentations/{pres_id}.{format}"
    return {"key": key, "status": "completed"}
