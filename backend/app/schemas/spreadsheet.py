from __future__ import annotations
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SpreadsheetCreate(BaseModel):
    title: str = Field(default="Untitled Spreadsheet", max_length=500)
    folder_id: uuid.UUID | None = None
    template_id: uuid.UUID | None = None


class SpreadsheetUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    folder_id: uuid.UUID | None = None
    sheets_meta_json: dict | None = None


class SpreadsheetResponse(BaseModel):
    id: uuid.UUID
    title: str
    owner_id: uuid.UUID
    folder_id: uuid.UUID | None = None
    sheets_meta_json: dict | None = None
    row_count: int
    col_count: int
    is_template: bool
    template_category: str | None = None
    thumbnail_key: str | None = None
    is_trashed: bool
    last_edited_by: uuid.UUID | None = None
    last_edited_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
