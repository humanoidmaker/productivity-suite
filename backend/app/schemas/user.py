from __future__ import annotations
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    avatar_url: str | None = None
    role: str
    storage_used: int
    storage_quota: int
    theme_preference: str
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    theme_preference: str | None = Field(None, pattern="^(light|dark|system)$")


class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(default="user", pattern="^(user|admin|superadmin)$")
    storage_quota: int = Field(default=524288000, ge=0)  # bytes


class AdminUpdateUserRequest(BaseModel):
    name: str | None = None
    role: str | None = Field(None, pattern="^(user|admin|superadmin)$")
    is_active: bool | None = None
    storage_quota: int | None = Field(None, ge=0)
