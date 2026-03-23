from __future__ import annotations
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ShareCreate(BaseModel):
    file_type: str = Field(pattern="^(document|spreadsheet|presentation)$")
    file_id: uuid.UUID
    shared_with_email: EmailStr | None = None
    permission: str = Field(default="view", pattern="^(view|comment|edit)$")
    password: str | None = None
    expires_at: datetime | None = None


class ShareLinkCreate(BaseModel):
    file_type: str = Field(pattern="^(document|spreadsheet|presentation)$")
    file_id: uuid.UUID
    permission: str = Field(default="view", pattern="^(view|comment|edit)$")
    password: str | None = None
    expires_at: datetime | None = None


class ShareUpdate(BaseModel):
    permission: str = Field(pattern="^(view|comment|edit)$")


class ShareResponse(BaseModel):
    id: uuid.UUID
    file_type: str
    file_id: uuid.UUID
    shared_by: uuid.UUID
    shared_with_user_id: uuid.UUID | None = None
    shared_with_email: str | None = None
    share_token: str | None = None
    permission: str
    expires_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
