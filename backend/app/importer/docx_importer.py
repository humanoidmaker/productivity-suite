from __future__ import annotations
"""Import DOCX to HTML using mammoth."""

import io


def import_docx(data: bytes) -> str:
    """Convert DOCX bytes to HTML string."""
    try:
        import mammoth
        result = mammoth.convert_to_html(io.BytesIO(data))
        return result.value
    except ImportError:
        # Fallback: use python-docx for basic extraction
        from docx import Document
        doc = Document(io.BytesIO(data))
        parts = []
        for para in doc.paragraphs:
            style = para.style.name.lower() if para.style else ""
            text = para.text
            if not text.strip():
                continue
            if "heading 1" in style:
                parts.append(f"<h1>{text}</h1>")
            elif "heading 2" in style:
                parts.append(f"<h2>{text}</h2>")
            elif "heading 3" in style:
                parts.append(f"<h3>{text}</h3>")
            elif "list" in style:
                parts.append(f"<li>{text}</li>")
            else:
                parts.append(f"<p>{text}</p>")
        return "\n".join(parts)
