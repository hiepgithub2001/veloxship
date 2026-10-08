"""Users admin API — list, create, update, reset password, soft-delete."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, require_role
from app.crud import audit as audit_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserCreated,
    UserOption,
    UserPage,
    UserRead,
    UserResetPasswordRequest,
    UserResetPasswordResponse,
    UserUpdate,
)
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserPage)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, min_length=1, max_length=100),
    role: str | None = Query(None),
    depot_id: int | None = Query(None),
    department: str | None = Query(None),
    position: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """List staff accounts with pagination and filters."""
    from app.crud import user as user_crud

    items, total = await user_crud.list_users(
        db,
        page=page,
        page_size=page_size,
        search=search,
        role=role,
        depot_id=depot_id,
        department=department,
        position=position,
        is_active=is_active,
    )
    return UserPage(
        items=[UserRead.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@router.post("", response_model=UserCreated, status_code=201)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Create a staff account (auto-generates a password when omitted)."""
    user, temporary_password = await user_service.create_user(db, body)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.user.create",
        entity_type="user",
        entity_id=user.id,
        details={"username": user.username, "role": user.role},
    )
    read = UserRead.model_validate(user)
    return UserCreated(**read.model_dump(), temporary_password=temporary_password)


@router.get("/options", response_model=list[UserOption])
async def user_options(
    search: str | None = Query(None, min_length=1, max_length=100),
    role: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a compact list of active users for picker selects (any authenticated user)."""
    from app.crud import user as user_crud

    items, _ = await user_crud.list_users(
        db, page=1, page_size=100, search=search, role=role, is_active=True
    )
    return [UserOption.model_validate(item) for item in items]


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Get a single staff account."""
    from app.crud import user as user_crud

    user = await user_crud.get_user(db, user_id)
    if user is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("USER_NOT_FOUND")
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Partially update a staff account."""
    user = await user_service.update_user(db, user_id, body, actor_id=current_user.id)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.user.update",
        entity_type="user",
        entity_id=user.id,
        details={"fields": list(body.model_dump(exclude_unset=True).keys())},
    )
    return UserRead.model_validate(user)


@router.post("/{user_id}/reset-password", response_model=UserResetPasswordResponse)
async def reset_password(
    user_id: int,
    body: UserResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Reset a staff account's password."""
    user, temporary_password = await user_service.reset_password(db, user_id, body.password)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.user.reset_password",
        entity_type="user",
        entity_id=user.id,
    )
    return UserResetPasswordResponse(temporary_password=temporary_password)


@router.delete("/{user_id}", response_model=UserRead)
async def soft_delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Soft-delete a staff account by deactivating it."""
    from app.schemas.user import UserUpdate as _Update

    user = await user_service.update_user(
        db, user_id, _Update(is_active=False), actor_id=current_user.id
    )
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.user.deactivate",
        entity_type="user",
        entity_id=user.id,
    )
    return UserRead.model_validate(user)
