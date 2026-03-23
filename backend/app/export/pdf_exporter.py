from __future__ import annotations
"""Export HTML content to PDF using WeasyPrint."""


def export_html_to_pdf(html: str, title: str = "Document") -> bytes:
    """Convert HTML to PDF bytes."""
    try:
        from weasyprint import HTML
    except ImportError:
        # WeasyPrint has system deps — fallback to simple error
        raise RuntimeError("WeasyPrint not installed. Install system dependencies: libpango, libcairo")

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            body {{ font-family: 'DejaVu Sans', sans-serif; font-size: 11pt; line-height: 1.5; margin: 1in; color: #333; }}
            h1 {{ font-size: 24pt; margin-top: 0; }}
            h2 {{ font-size: 18pt; }}
            h3 {{ font-size: 14pt; }}
            pre, code {{ font-family: 'DejaVu Sans Mono', monospace; font-size: 9pt; background: #f5f5f5; padding: 8px; border-radius: 4px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            td, th {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; }}
            th {{ background: #f0f0f0; font-weight: bold; }}
            blockquote {{ border-left: 3px solid #ccc; padding-left: 12px; margin-left: 0; color: #666; }}
            img {{ max-width: 100%; }}
        </style>
    </head>
    <body>{html}</body>
    </html>
    """
    pdf_bytes = HTML(string=full_html).write_pdf()
    return pdf_bytes
