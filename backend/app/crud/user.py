"""User CRUD operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User


async def get_by_username(db: AsyncSession, username: str) -> User | None:
    """Fetch a user by username (case-insensitive)."""
    result = await db.execute(
        select(User).where(User.username == username.lower())
    )
    return result.scalar_one_or_none()


async def authenticate(db: AsyncSession, username: str, password: str) -> User | None:
    """Verify credentials and return the user, or None if invalid."""
    user = await get_by_username(db, username)
    if user is None or not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


async def create_user(
    db: AsyncSession,
    *,
    username: str,
    full_name: str,
    password: str,
    role: str = "staff",
) -> User:
    """Create a new user with hashed password."""
    user = User(
        username=username.lower(),
        full_name=full_name,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    await db.flush()
    return user
