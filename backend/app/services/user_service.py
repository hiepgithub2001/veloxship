"""Staff account business logic — create, update, reset password, self-service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.core.security import generate_password, hash_password, verify_password
from app.crud import permission as permission_crud
from app.crud import user as user_crud
from app.models.depot import Depot
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, ProfileUpdate
from app.schemas.user import UserCreate, UserUpdate


async def _validate_depot(db: AsyncSession, depot_id: int | None) -> None:
    """Raise NotFoundError if depot_id does not reference an active depot."""
    if depot_id is None:
        return
    result = await db.execute(select(Depot).where(Depot.id == depot_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundError("DEPOT_NOT_FOUND")


async def _validate_role(db: AsyncSession, role: str) -> None:
    """Raise when `role` does not reference an active role."""
    role_obj = await permission_crud.get_role(db, role)
    if role_obj is None:
        raise NotFoundError("ROLE_NOT_FOUND")
    if not role_obj.is_active:
        raise AppError("ROLE_INACTIVE", status_code=400)


async def create_user(
    db: AsyncSession, payload: UserCreate
) -> tuple[User, str | None]:
    """Create a staff account; returns (user, temporary_password)."""
    username = payload.username
    if await user_crud.get_by_username(db, username) is not None:
        raise ConflictError("USERNAME_EXISTS")
    if payload.phone and await user_crud.get_by_phone(db, payload.phone) is not None:
        raise ConflictError("PHONE_EXISTS")

    await _validate_depot(db, payload.depot_id)
    await _validate_role(db, payload.role)

    temporary_password = None
    password = payload.password
    if password is None:
        temporary_password = generate_password()
        password = temporary_password

    user = await user_crud.create_user(
        db,
        username=username,
        full_name=payload.full_name,
        password_hash=hash_password(password),
        role=payload.role,
        phone=payload.phone,
        department=payload.department,
        position=payload.position,
        employee_code=payload.employee_code,
        depot_id=payload.depot_id,
    )
    # Re-read with relationships populated.
    return await user_crud.get_user(db, user.id), temporary_password


async def update_user(
    db: AsyncSession, user_id: int, payload: UserUpdate, *, actor_id: int
) -> User:
    """Update a staff account; returns the updated user."""
    user = await user_crud.get_user(db, user_id)
    if user is None:
        raise NotFoundError("USER_NOT_FOUND")

    data = payload.model_dump(exclude_unset=True)

    if "phone" in data and data["phone"]:
        existing = await user_crud.get_by_phone(db, data["phone"])
        if existing is not None and existing.id != user.id:
            raise ConflictError("PHONE_EXISTS")

    if "depot_id" in data:
        await _validate_depot(db, data["depot_id"])

    if "role" in data:
        await _validate_role(db, data["role"])

    # Prevent an admin from locking their own account.
    if data.get("is_active") is False and user.id == actor_id:
        raise AppError("CANNOT_LOCK_SELF", status_code=409)

    if data:
        await user_crud.update_user(db, user=user, data=data)

    return await user_crud.get_user(db, user.id)


async def reset_password(
    db: AsyncSession, user_id: int, password: str | None
) -> tuple[User, str]:
    """Reset a user's password; returns (user, temporary_password)."""
    user = await user_crud.get_user(db, user_id)
    if user is None:
        raise NotFoundError("USER_NOT_FOUND")

    temporary_password = password or generate_password()
    await user_crud.set_password(db, user=user, password=temporary_password)
    return await user_crud.get_user(db, user.id), temporary_password


async def update_profile(
    db: AsyncSession, user: User, payload: ProfileUpdate
) -> User:
    """Update a user's own profile (full_name, phone, avatar); returns the user."""
    data = payload.model_dump(exclude_unset=True)

    if "phone" in data and data["phone"]:
        existing = await user_crud.get_by_phone(db, data["phone"])
        if existing is not None and existing.id != user.id:
            raise ConflictError("PHONE_EXISTS")

    if data:
        await user_crud.update_user(db, user=user, data=data)

    return await user_crud.get_user(db, user.id)


async def change_password(
    db: AsyncSession, user: User, payload: ChangePasswordRequest
) -> User:
    """Change a user's own password after verifying the current one."""
    if not verify_password(payload.current_password, user.password_hash):
        raise AppError("CURRENT_PASSWORD_INCORRECT", status_code=400)
    if verify_password(payload.new_password, user.password_hash):
        raise AppError("NEW_PASSWORD_SAME_AS_CURRENT", status_code=400)

    await user_crud.set_password(db, user=user, password=payload.new_password)
    return await user_crud.get_user(db, user.id)
