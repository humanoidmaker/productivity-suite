from __future__ import annotations
"""Detect file type from content, validate, size check."""

# Magic bytes for common file types
SIGNATURES = {
    b"PK\x03\x04": "zip",  # DOCX, XLSX, PPTX are all ZIP-based
    b"%PDF": "pdf",
    b"\xff\xd8\xff": "jpeg",
    b"\x89PNG": "png",
    b"GIF8": "gif",
}

OFFICE_CONTENT_TYPES = {
    "word/document.xml": "docx",
    "xl/workbook.xml": "xlsx",
    "ppt/presentation.xml": "pptx",
}


def detect_file_type(data: bytes) -> str | None:
    """Detect file type from magic bytes."""
    for sig, file_type in SIGNATURES.items():
        if data[:len(sig)] == sig:
            if file_type == "zip":
                return _detect_office_type(data)
            return file_type
    # Check if it's text-based
    try:
        data[:1000].decode("utf-8")
        if data.strip().startswith(b"<"):
            return "html"
        return "text"
    except UnicodeDecodeError:
        return None


def _detect_office_type(data: bytes) -> str:
    """Detect specific Office format from ZIP-based file."""
    import zipfile
    import io
    try:
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            names = zf.namelist()
            for content_path, file_type in OFFICE_CONTENT_TYPES.items():
                if content_path in names:
                    return file_type
    except zipfile.BadZipFile:
        pass
    return "zip"


def validate_file(data: bytes, max_size_mb: int = 50) -> tuple[bool, str]:
    """Validate file size and type. Returns (valid, error_message)."""
    if len(data) > max_size_mb * 1024 * 1024:
        return False, f"File too large (max {max_size_mb}MB)"
    if len(data) == 0:
        return False, "File is empty"
    file_type = detect_file_type(data)
    if file_type is None:
        return False, "Unknown file type"
    return True, ""
