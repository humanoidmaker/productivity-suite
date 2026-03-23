from __future__ import annotations
"""Cleanup tasks — purge old trash, clean orphan assets."""
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.cleanup_tasks.purge_old_trash")
def purge_old_trash() -> dict:
    """Purge trash items older than configured days."""
    # In production: use sync DB session, call trash_service.purge_old_trash
    return {"purged": 0}


@celery_app.task(name="app.tasks.cleanup_tasks.clean_orphan_assets")
def clean_orphan_assets() -> dict:
    """Remove assets not referenced by any document."""
    return {"cleaned": 0}
