from __future__ import annotations
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    file_type: str = Field(pattern="^(document|spreadsheet|presentation)$")
    category: str = Field(default="blank", max_length=50)
    is_public: bool = False


class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    file_type: str
    preview_image_key: str | None = None
    category: str
    created_by: uuid.UUID | None = None
    is_public: bool
    created_at: datetime
    preview_url: str | None = None  # Presigned URL

    model_config = {"from_attributes": True}
