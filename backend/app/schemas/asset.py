from __future__ import annotations
import uuid
from datetime import datetime

from pydantic import BaseModel


class AssetResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    file_name: str
    mime_type: str
    size: int
    storage_key: str
    thumbnail_key: str | None = None
    created_at: datetime
    url: str | None = None  # Presigned URL, populated in API

    model_config = {"from_attributes": True}
