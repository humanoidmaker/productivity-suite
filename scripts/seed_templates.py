"""Seed default templates for all three apps."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import get_settings
from app.database import async_session_factory
from app.models import Template
from app.utils.minio_client import upload_bytes
from sqlalchemy import select

TEMPLATES = [
    # Documents
    {"name": "Blank Document", "file_type": "document", "category": "blank"},
    {"name": "Business Letter", "file_type": "document", "category": "business"},
    {"name": "Meeting Notes", "file_type": "document", "category": "business"},
    {"name": "Project Proposal", "file_type": "document", "category": "business"},
    {"name": "Resume", "file_type": "document", "category": "personal"},
    {"name": "Report", "file_type": "document", "category": "business"},
    {"name": "Invoice", "file_type": "document", "category": "business"},
    # Spreadsheets
    {"name": "Blank Spreadsheet", "file_type": "spreadsheet", "category": "blank"},
    {"name": "Budget Tracker", "file_type": "spreadsheet", "category": "personal"},
    {"name": "Project Timeline", "file_type": "spreadsheet", "category": "business"},
    {"name": "Expense Report", "file_type": "spreadsheet", "category": "business"},
    {"name": "Grade Book", "file_type": "spreadsheet", "category": "education"},
    {"name": "Inventory", "file_type": "spreadsheet", "category": "business"},
    # Presentations
    {"name": "Blank Presentation", "file_type": "presentation", "category": "blank"},
    {"name": "Business Pitch", "file_type": "presentation", "category": "business"},
    {"name": "Quarterly Review", "file_type": "presentation", "category": "business"},
    {"name": "Product Launch", "file_type": "presentation", "category": "business"},
    {"name": "Education", "file_type": "presentation", "category": "education"},
    {"name": "Portfolio", "file_type": "presentation", "category": "personal"},
    {"name": "Conference Talk", "file_type": "presentation", "category": "business"},
]


async def main():
    settings = get_settings()

    async with async_session_factory() as db:
        for tpl in TEMPLATES:
            existing = await db.execute(select(Template).where(Template.name == tpl["name"], Template.file_type == tpl["file_type"]))
            if existing.scalar_one_or_none():
                continue

            # Create empty content snapshot
            key = f"templates/{tpl['file_type']}/{tpl['name'].lower().replace(' ', '_')}.bin"
            try:
                upload_bytes(settings.minio_bucket_snapshots, key, b"")
            except Exception:
                pass  # MinIO may not be available

            template = Template(
                name=tpl["name"],
                file_type=tpl["file_type"],
                category=tpl["category"],
                content_snapshot_key=key,
                is_public=True,
            )
            db.add(template)

        await db.commit()
        print(f"Seeded {len(TEMPLATES)} templates.")


if __name__ == "__main__":
    asyncio.run(main())
