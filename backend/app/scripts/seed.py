"""Seed script — creates admin user and verifies service-tier seed.

Run: python -m app.scripts.seed
"""

import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import async_session_factory
from app.models.service_tier import ServiceTier
from app.models.user import User


async def seed() -> None:
    async with async_session_factory() as db:
        # Check if admin already exists
        result = await db.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none() is None:
            admin = User(
                username="admin",
                full_name="Quản trị viên",
                password_hash=hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            print("✓ Admin user created (admin / admin123)")
        else:
            print("• Admin user already exists, skipping.")

        # Verify service tiers are seeded
        result = await db.execute(select(ServiceTier))
        tiers = result.scalars().all()
        print(f"• {len(tiers)} service tiers in database.")

        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
