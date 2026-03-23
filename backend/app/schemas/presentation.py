from __future__ import annotations
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PresentationCreate(BaseModel):
    title: str = Field(default="Untitled Presentation", max_length=500)
    folder_id: uuid.UUID | None = None
    aspect_ratio: str = Field(default="16:9", pattern="^(16:9|4:3)$")
    template_id: uuid.UUID | None = None


class PresentationUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    folder_id: uuid.UUID | None = None
    slides_meta_json: dict | None = None
    theme_json: dict | None = None
    aspect_ratio: str | None = Field(None, pattern="^(16:9|4:3)$")


class PresentationResponse(BaseModel):
    id: uuid.UUID
    title: str
    owner_id: uuid.UUID
    folder_id: uuid.UUID | None = None
    slides_meta_json: dict | None = None
    slide_count: int
    theme_json: dict | None = None
    aspect_ratio: str
    is_template: bool
    template_category: str | None = None
    thumbnail_key: str | None = None
    is_trashed: bool
    last_edited_by: uuid.UUID | None = None
    last_edited_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
