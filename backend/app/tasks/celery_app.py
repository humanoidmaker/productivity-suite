from __future__ import annotations
from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "productivity",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Periodic tasks
celery_app.conf.beat_schedule = {
    "snapshot-active-documents": {
        "task": "app.tasks.snapshot_tasks.create_periodic_snapshots",
        "schedule": settings.version_snapshot_interval_minutes * 60,
    },
    "cleanup-trash": {
        "task": "app.tasks.cleanup_tasks.purge_old_trash",
        "schedule": crontab(hour=3, minute=0),  # daily at 3 AM
    },
    "daily-storage-stats": {
        "task": "app.tasks.stats_tasks.aggregate_storage_stats",
        "schedule": crontab(hour=2, minute=0),  # daily at 2 AM
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "app.tasks.export_tasks",
    "app.tasks.import_tasks",
    "app.tasks.snapshot_tasks",
    "app.tasks.thumbnail_tasks",
    "app.tasks.cleanup_tasks",
    "app.tasks.stats_tasks",
])
