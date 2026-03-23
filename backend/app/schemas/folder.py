import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FolderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    parent_folder_id: uuid.UUID | None = None
    color: str | None = None
    icon: str | None = None


class FolderUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    color: str | None = None
    icon: str | None = None


class FolderMove(BaseModel):
    parent_folder_id: uuid.UUID | None = None


class FolderResponse(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    parent_folder_id: uuid.UUID | None = None
    color: str | None = None
    icon: str | None = None
    is_trashed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BreadcrumbItem(BaseModel):
    id: uuid.UUID
    name: str
