from __future__ import annotations
"""Yjs awareness protocol — cursor/selection sharing between collaborators."""

import json
from typing import Any


def encode_awareness_update(user_id: str, name: str, color: str, cursor: dict | None = None, selection: dict | None = None) -> bytes:
    """Encode an awareness state update as bytes for broadcasting."""
    state = {
        "user": {"id": user_id, "name": name, "color": color},
        "cursor": cursor,
        "selection": selection,
    }
    return json.dumps({"type": "awareness", "state": state}).encode()


def decode_awareness_update(data: bytes) -> dict | None:
    """Decode an awareness update from bytes."""
    try:
        msg = json.loads(data)
        if msg.get("type") == "awareness":
            return msg.get("state")
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    return None
