"""Seed script — creates admin user, service tiers, default roles, and role permissions.

Run: python -m app.scripts.seed
"""

import asyncio

from sqlalchemy import select

from app.core.permissions import ROLE_DEFAULT_PERMISSIONS, default_roles
from app.core.security import hash_password
from app.db.session import async_session_factory
from app.models.permission import Role, RolePermission
from app.models.service_tier import ServiceTier
from app.models.user import User


async def seed_roles(db) -> None:
    """Create default roles + their role_permissions (idempotent)."""
    for item in default_roles():
        code = item["code"]
        result = await db.execute(select(Role).where(Role.code == code))
        role = result.scalar_one_or_none()
        if role is None:
            role = Role(code=code, name=item["name"])
            db.add(role)
            await db.flush()
            print(f"✓ Role created: {code}")
        else:
            print(f"• Role already exists: {code}")

        # Ensure the role has at least its default actions (never removes extras).
        existing = {p.action for p in role.permissions}
        for action in ROLE_DEFAULT_PERMISSIONS.get(code, []):
            if action not in existing:
                role.permissions.append(RolePermission(role=code, action=action))
        await db.flush()


async def seed() -> None:
    async with async_session_factory() as db:
        # Roles must exist first — users.role is now a FK to roles.code.
        await seed_roles(db)

        # Ensure the admin account exists with the default credentials.
        result = await db.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        if admin is None:
            admin = User(
                username="admin",
                full_name="Quản trị viên",
                password_hash=hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            await db.flush()
            print("✓ Admin user created (admin / admin123)")
        else:
            admin.password_hash = hash_password("admin123")
            admin.role = "admin"
            admin.is_active = True
            await db.flush()
            print("✓ Admin user reset (admin / admin123)")

        # Verify service tiers are seeded
        result = await db.execute(select(ServiceTier))
        tiers = result.scalars().all()
        print(f"• {len(tiers)} service tiers in database.")

        await db.commit()

    # Seed administrative divisions (provinces & wards)
    from app.scripts.seed_divisions import seed_divisions
    await seed_divisions()


if __name__ == "__main__":
    asyncio.run(seed())
