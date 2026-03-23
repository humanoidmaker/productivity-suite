from __future__ import annotations
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    file_type: str = Field(pattern="^(document|spreadsheet|presentation)$")
    file_id: uuid.UUID
    content: str = Field(min_length=1, max_length=5000)
    position_json: dict | None = None
    parent_comment_id: uuid.UUID | None = None


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    id: uuid.UUID
    file_type: str
    file_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    position_json: dict | None = None
    parent_comment_id: uuid.UUID | None = None
    resolved: bool
    resolved_by: uuid.UUID | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    # Populated in API
    author_name: str | None = None
    author_avatar: str | None = None

    model_config = {"from_attributes": True}
