from __future__ import annotations
"""Daily stats aggregation tasks."""
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.stats_tasks.aggregate_storage_stats")
def aggregate_storage_stats() -> dict:
    """Recalculate storage usage for all users."""
    # In production: iterate users, refresh storage_used from assets
    return {"users_updated": 0}
