from __future__ import annotations
"""Collaboration service — Yjs document management, room tracking."""

import uuid
from dataclasses import dataclass, field


@dataclass
class Collaborator:
    user_id: uuid.UUID
    name: str
    avatar_url: str | None = None
    color: str = "#3b82f6"
    cursor_position: dict | None = None
    selection_range: dict | None = None


@dataclass
class CollabRoom:
    file_type: str
    file_id: uuid.UUID
    collaborators: dict[uuid.UUID, Collaborator] = field(default_factory=dict)

    @property
    def count(self) -> int:
        return len(self.collaborators)


# Assigned colors for collaborators
COLLAB_COLORS = [
    "#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6",
    "#ec4899", "#06b6d4", "#f97316", "#14b8a6", "#a855f7",
    "#6366f1", "#84cc16", "#e11d48", "#0ea5e9", "#d946ef",
    "#65a30d", "#dc2626", "#0891b2", "#c026d3", "#ea580c",
]


class CollaborationManager:
    """In-memory collaboration room manager."""

    def __init__(self):
        self._rooms: dict[str, CollabRoom] = {}

    def _room_key(self, file_type: str, file_id: uuid.UUID) -> str:
        return f"{file_type}:{file_id}"

    def join_room(self, file_type: str, file_id: uuid.UUID, user_id: uuid.UUID, name: str, avatar_url: str | None = None) -> Collaborator:
        key = self._room_key(file_type, file_id)
        if key not in self._rooms:
            self._rooms[key] = CollabRoom(file_type=file_type, file_id=file_id)
        room = self._rooms[key]
        color_idx = len(room.collaborators) % len(COLLAB_COLORS)
        collab = Collaborator(user_id=user_id, name=name, avatar_url=avatar_url, color=COLLAB_COLORS[color_idx])
        room.collaborators[user_id] = collab
        return collab

    def leave_room(self, file_type: str, file_id: uuid.UUID, user_id: uuid.UUID) -> None:
        key = self._room_key(file_type, file_id)
        room = self._rooms.get(key)
        if room:
            room.collaborators.pop(user_id, None)
            if not room.collaborators:
                del self._rooms[key]

    def get_room(self, file_type: str, file_id: uuid.UUID) -> CollabRoom | None:
        return self._rooms.get(self._room_key(file_type, file_id))

    def get_collaborators(self, file_type: str, file_id: uuid.UUID) -> list[Collaborator]:
        room = self.get_room(file_type, file_id)
        return list(room.collaborators.values()) if room else []

    def update_cursor(self, file_type: str, file_id: uuid.UUID, user_id: uuid.UUID, cursor: dict | None = None, selection: dict | None = None) -> None:
        room = self.get_room(file_type, file_id)
        if room and user_id in room.collaborators:
            if cursor is not None:
                room.collaborators[user_id].cursor_position = cursor
            if selection is not None:
                room.collaborators[user_id].selection_range = selection

    def active_room_count(self) -> int:
        return len(self._rooms)

    def total_connections(self) -> int:
        return sum(room.count for room in self._rooms.values())


# Singleton
collab_manager = CollaborationManager()
