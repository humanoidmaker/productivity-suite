from __future__ import annotations
import secrets
import uuid
from pathlib import PurePosixPath

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
ALLOWED_IMPORT_TYPES = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".csv": "text/csv",
}

FILE_TYPE_EXTENSIONS = {
    "document": [".docx", ".pdf", ".html", ".md", ".txt"],
    "spreadsheet": [".xlsx", ".csv", ".pdf"],
    "presentation": [".pptx", ".pdf", ".png", ".jpg"],
}


def generate_storage_key(prefix: str, filename: str) -> str:
    """Generate a unique storage key: prefix/uuid/filename"""
    uid = uuid.uuid4().hex[:12]
    safe_name = PurePosixPath(filename).name
    return f"{prefix}/{uid}/{safe_name}"


def generate_share_token() -> str:
    """Generate a URL-safe share token."""
    return secrets.token_urlsafe(32)


def is_valid_image_type(mime_type: str) -> bool:
    return mime_type in ALLOWED_IMAGE_TYPES


def get_file_extension(filename: str) -> str:
    return PurePosixPath(filename).suffix.lower()


def validate_file_size(size: int, max_mb: int) -> bool:
    return size <= max_mb * 1024 * 1024


def sanitize_filename(filename: str) -> str:
    """Remove path separators and null bytes from filename."""
    name = PurePosixPath(filename).name
    return name.replace("\x00", "").strip()
