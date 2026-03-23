from __future__ import annotations
"""Export document as standalone HTML file."""


def export_standalone_html(content_html: str, title: str = "Document") -> str:
    """Wrap content HTML in a standalone HTML document."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 16px; line-height: 1.6; color: #1a1a1a; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1 {{ font-size: 2em; margin: 1em 0 0.5em; }}
        h2 {{ font-size: 1.5em; margin: 1em 0 0.5em; }}
        h3 {{ font-size: 1.25em; margin: 1em 0 0.5em; }}
        p {{ margin: 0.5em 0; }}
        ul, ol {{ margin: 0.5em 0; padding-left: 2em; }}
        li {{ margin: 0.25em 0; }}
        pre {{ background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 6px; padding: 16px; overflow-x: auto; font-size: 14px; }}
        code {{ font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; background: #f6f8fa; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
        pre code {{ background: none; padding: 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
        td, th {{ border: 1px solid #d0d7de; padding: 8px 12px; text-align: left; }}
        th {{ background: #f6f8fa; font-weight: 600; }}
        blockquote {{ border-left: 4px solid #d0d7de; padding-left: 16px; margin: 1em 0; color: #57606a; }}
        img {{ max-width: 100%; height: auto; border-radius: 4px; }}
        hr {{ border: none; border-top: 1px solid #d0d7de; margin: 2em 0; }}
        a {{ color: #0969da; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
{content_html}
</body>
</html>"""
