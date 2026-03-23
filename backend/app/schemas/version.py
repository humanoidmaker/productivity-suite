from __future__ import annotations
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class VersionCreate(BaseModel):
    name: str | None = Field(None, max_length=255)


class VersionResponse(BaseModel):
    id: uuid.UUID
    file_type: str
    file_id: uuid.UUID
    version_number: int
    title_at_version: str
    name: str | None = None
    created_by: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
