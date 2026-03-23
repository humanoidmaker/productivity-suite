from __future__ import annotations
"""Presence tracking — active users per document with cursor and selection info."""

import uuid
from dataclasses import dataclass


@dataclass
class UserPresence:
    user_id: uuid.UUID
    name: str
    avatar_url: str | None
    color: str
    cursor_position: dict | None = None
    selection_range: dict | None = None

    def to_dict(self) -> dict:
        return {
            "user_id": str(self.user_id),
            "name": self.name,
            "avatar_url": self.avatar_url,
            "color": self.color,
            "cursor_position": self.cursor_position,
            "selection_range": self.selection_range,
        }
