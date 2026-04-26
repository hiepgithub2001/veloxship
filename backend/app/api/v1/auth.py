"""Auth API — login, refresh, me."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.i18n import get_message
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.crud import audit as audit_crud
from app.crud import user as user_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenPair, UserRead

from .deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


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


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return current_user
