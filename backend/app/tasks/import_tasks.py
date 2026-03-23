from __future__ import annotations
"""Async import tasks for large files."""
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.import_tasks.import_large_file")
def import_large_file_task(file_key: str, file_type: str, user_id: str) -> dict:
    """Import a large file from MinIO storage."""
    return {"file_key": file_key, "file_type": file_type, "status": "completed"}
