from __future__ import annotations
"""Periodic version snapshot tasks."""
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.snapshot_tasks.create_periodic_snapshots")
def create_periodic_snapshots() -> dict:
    """Create snapshots for all documents with active collaboration sessions."""
    from app.services.collaboration_service import collab_manager
    active_rooms = collab_manager.active_room_count()
    # In production: iterate active rooms, fetch Yjs state, create snapshots via version_service
    return {"active_rooms": active_rooms, "snapshots_created": 0}
