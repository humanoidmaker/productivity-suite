from typing import Optional
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, LargeBinary, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Spreadsheet(Base):
    __tablename__ = "spreadsheets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="Untitled Spreadsheet")
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    folder_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("folders.id", ondelete="SET NULL"), nullable=True, index=True)
    sheets_yjs: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)  # Binary Yjs state for all sheets
    sheets_meta_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # sheet names, order, visibility, color tabs
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    col_count: Mapped[int] = mapped_column(Integer, nullable=False, default=26)
    is_template: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    template_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    thumbnail_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_trashed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    trashed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_edited_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="spreadsheets", foreign_keys=[owner_id])
    folder = relationship("Folder")
