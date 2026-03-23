"""Seed the initial superadmin user."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import get_settings
from app.database import engine, async_session_factory, Base
from app.models import User
from app.utils.hashing import hash_password
from sqlalchemy import select


async def main():
    settings = get_settings()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.email == "admin@productivity.local"))
        if result.scalar_one_or_none():
            print("Admin user already exists.")
            return

        admin = User(
            email="admin@productivity.local",
            name="Admin",
            password_hash=hash_password("admin123"),
            role="superadmin",
            storage_quota=10 * 1024 * 1024 * 1024,  # 10 GB
        )
        db.add(admin)
        await db.commit()
        print(f"Created superadmin: admin@productivity.local / admin123")


if __name__ == "__main__":
    asyncio.run(main())
