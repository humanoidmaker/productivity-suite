from __future__ import annotations
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str = Field(default="Untitled Document", max_length=500)
    folder_id: uuid.UUID | None = None
    template_id: uuid.UUID | None = None


class DocumentUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    folder_id: uuid.UUID | None = None
    content_html: str | None = None
    page_settings_json: dict | None = None


class DocumentResponse(BaseModel):
    id: uuid.UUID
    title: str
    owner_id: uuid.UUID
    folder_id: uuid.UUID | None = None
    word_count: int
    char_count: int
    page_settings_json: dict | None = None
    is_template: bool
    template_category: str | None = None
    thumbnail_key: str | None = None
    is_trashed: bool
    last_edited_by: uuid.UUID | None = None
    last_edited_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentContentResponse(BaseModel):
    id: uuid.UUID
    title: str
    content_html: str | None = None
    content_yjs_base64: str | None = None  # base64-encoded Yjs state for editor init
    page_settings_json: dict | None = None
