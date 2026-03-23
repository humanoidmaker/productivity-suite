from __future__ import annotations
import uuid
from datetime import datetime

from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class IdResponse(BaseModel):
    id: uuid.UUID


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime
