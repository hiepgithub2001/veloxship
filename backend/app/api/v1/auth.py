"""Auth API — login, refresh, me, and self-service account management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.i18n import get_message
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.crud import audit as audit_crud
from app.crud import permission as permission_crud
from app.crud import user as user_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    LoginRequest,
    ProfileUpdate,
    RefreshRequest,
    TokenPair,
    UserMe,
)
from app.services import user_service

from .deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


async def _build_user_me(db: AsyncSession, user: User) -> UserMe:
    """Compose the current-user read model with effective permissions."""
    actions = await permission_crud.get_role_permission_actions(db, user.role)
    return UserMe(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        avatar=user.avatar,
        role=user.role,
        is_active=user.is_active,
        department=user.department,
        position=user.position,
        employee_code=user.employee_code,
        depot_id=user.depot_id,
        permissions=sorted(actions),
    )


@router.post("/login", response_model=TokenPair)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return a token pair."""
    user = await user_crud.authenticate(db, body.username, body.password)
    if user is None:
        await audit_crud.log_event(
            db,
            actor_id=None,
            action="auth.failed_login",
            details={"username": body.username},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message("INVALID_CREDENTIALS"),
        )

    await audit_crud.log_event(
        db,
        actor_id=user.id,
        action="auth.login",
        entity_type="user",
        entity_id=user.id,
    )

    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id, user.username)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_TTL_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh the access token using a valid refresh token."""
    from jose import JWTError

    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=get_message("TOKEN_INVALID"),
            )
        user_id = int(payload["sub"])
        username = payload["username"]
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message("TOKEN_INVALID"),
        )

    # Verify user still exists and is active
    user = await user_crud.get_by_username(db, username)
    if user is None or not user.is_active or user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message("TOKEN_INVALID"),
        )

    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id, user.username)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_TTL_MINUTES * 60,
    )


@router.get("/me", response_model=UserMe)
async def me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the currently authenticated user plus effective permissions."""
    return await _build_user_me(db, current_user)


@router.patch("/me", response_model=UserMe)
async def update_me(
    body: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the current user's own profile (full_name, phone, avatar)."""
    user = await user_service.update_profile(db, current_user, body)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.profile.update",
        entity_type="user",
        entity_id=user.id,
        details={"fields": list(body.model_dump(exclude_unset=True).keys())},
    )
    return await _build_user_me(db, user)


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    body: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change the current user's own password after verifying the current one."""
    await user_service.change_password(db, current_user, body)
    await audit_crud.log_event(
        db,
        actor_id=current_user.id,
        action="iam.password.change",
        entity_type="user",
        entity_id=current_user.id,
    )
    return ChangePasswordResponse(message=get_message("PASSWORD_CHANGED"))
