from __future__ import annotations
"""Yjs document manager — loads from DB on first connect, persists on disconnect/interval."""

import uuid
from typing import Any


class YjsDocumentManager:
    """Manages Yjs document instances in memory."""

    def __init__(self):
        self._docs: dict[str, bytes] = {}  # room_key -> Yjs state bytes

    def _key(self, file_type: str, file_id: uuid.UUID) -> str:
        return f"{file_type}:{file_id}"

    def get_state(self, file_type: str, file_id: uuid.UUID) -> bytes | None:
        return self._docs.get(self._key(file_type, file_id))

    def set_state(self, file_type: str, file_id: uuid.UUID, state: bytes) -> None:
        self._docs[self._key(file_type, file_id)] = state

    def apply_update(self, file_type: str, file_id: uuid.UUID, update: bytes) -> None:
        """Apply a Yjs update to the document state."""
        key = self._key(file_type, file_id)
        # In production, use pycrdt to merge the update into the current state
        # For now, just store the latest update
        current = self._docs.get(key, b"")
        self._docs[key] = current + update  # Simplified — real impl uses Yjs merge

    def remove(self, file_type: str, file_id: uuid.UUID) -> bytes | None:
        """Remove and return the final state for persistence."""
        return self._docs.pop(self._key(file_type, file_id), None)

    def has_document(self, file_type: str, file_id: uuid.UUID) -> bool:
        return self._key(file_type, file_id) in self._docs

    def active_count(self) -> int:
        return len(self._docs)


yjs_manager = YjsDocumentManager()
