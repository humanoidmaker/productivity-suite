from __future__ import annotations
"""WebSocket connection handler — auth, room join/leave, message routing."""

import uuid
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket


@dataclass
class WSConnection:
    ws: WebSocket
    user_id: uuid.UUID
    user_name: str
    file_type: str
    file_id: uuid.UUID


class WSConnectionManager:
    """Track WebSocket connections per room."""

    def __init__(self):
        self._rooms: dict[str, list[WSConnection]] = {}

    def _key(self, file_type: str, file_id: uuid.UUID) -> str:
        return f"{file_type}:{file_id}"

    async def connect(self, conn: WSConnection) -> None:
        key = self._key(conn.file_type, conn.file_id)
        if key not in self._rooms:
            self._rooms[key] = []
        self._rooms[key].append(conn)

    async def disconnect(self, conn: WSConnection) -> None:
        key = self._key(conn.file_type, conn.file_id)
        if key in self._rooms:
            self._rooms[key] = [c for c in self._rooms[key] if c.user_id != conn.user_id]
            if not self._rooms[key]:
                del self._rooms[key]

    async def broadcast_to_room(self, file_type: str, file_id: uuid.UUID, data: bytes, exclude_user: uuid.UUID | None = None) -> None:
        key = self._key(file_type, file_id)
        for conn in self._rooms.get(key, []):
            if conn.user_id != exclude_user:
                try:
                    await conn.ws.send_bytes(data)
                except Exception:
                    pass

    def get_room_connections(self, file_type: str, file_id: uuid.UUID) -> list[WSConnection]:
        return self._rooms.get(self._key(file_type, file_id), [])

    def total_connections(self) -> int:
        return sum(len(conns) for conns in self._rooms.values())


ws_manager = WSConnectionManager()
