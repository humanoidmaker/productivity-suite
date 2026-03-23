from __future__ import annotations
"""WebSocket endpoint for real-time Yjs sync and presence."""

import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.user import User
from app.services.collaboration_service import collab_manager
from app.utils.tokens import decode_access_token

router = APIRouter(tags=["collaboration"])

# Active WebSocket connections per room
_connections: dict[str, dict[uuid.UUID, WebSocket]] = {}


def _room_key(file_type: str, file_id: str) -> str:
    return f"{file_type}:{file_id}"


@router.websocket("/ws/collab/{file_type}/{file_id}")
async def collaboration_ws(ws: WebSocket, file_type: str, file_id: str, token: str = Query(...)):
    # Authenticate
    try:
        payload = decode_access_token(token)
        user_id = uuid.UUID(payload["sub"])
    except Exception:
        await ws.close(code=4001, reason="Invalid token")
        return

    # Get user info
    async with async_session_factory() as db:
        result = await db.execute(select(User.name, User.avatar_url).where(User.id == user_id))
        row = result.one_or_none()
        if not row:
            await ws.close(code=4002, reason="User not found")
            return
        user_name, avatar_url = row

    await ws.accept()

    # Join room
    key = _room_key(file_type, file_id)
    collab = collab_manager.join_room(file_type, uuid.UUID(file_id), user_id, user_name, avatar_url)

    if key not in _connections:
        _connections[key] = {}
    _connections[key][user_id] = ws

    # Broadcast presence update
    await _broadcast_presence(key, file_type, file_id)

    try:
        while True:
            data = await ws.receive_bytes()
            # Broadcast Yjs update to all other clients in the room
            for uid, conn in _connections.get(key, {}).items():
                if uid != user_id:
                    try:
                        await conn.send_bytes(data)
                    except Exception:
                        pass
    except WebSocketDisconnect:
        pass
    finally:
        # Leave room
        collab_manager.leave_room(file_type, uuid.UUID(file_id), user_id)
        _connections.get(key, {}).pop(user_id, None)
        if key in _connections and not _connections[key]:
            del _connections[key]
        await _broadcast_presence(key, file_type, file_id)


async def _broadcast_presence(key: str, file_type: str, file_id: str) -> None:
    """Broadcast current collaborator list to all clients in room."""
    collaborators = collab_manager.get_collaborators(file_type, uuid.UUID(file_id))
    presence_data = json.dumps({
        "type": "presence",
        "collaborators": [
            {"user_id": str(c.user_id), "name": c.name, "avatar_url": c.avatar_url, "color": c.color}
            for c in collaborators
        ],
    }).encode()

    for conn in _connections.get(key, {}).values():
        try:
            await conn.send_bytes(presence_data)
        except Exception:
            pass
