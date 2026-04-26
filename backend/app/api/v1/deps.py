"""FastAPI dependencies — authentication and authorization."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import get_message
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT bearer token, load the user, and return it.

    Raises 401 with Vietnamese message on any failure.
    """
    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=get_message("TOKEN_INVALID"),
            )
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message("TOKEN_INVALID"),
        )

    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message("UNAUTHORIZED"),
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_message("USER_INACTIVE"),
        )
    return user


def require_role(*roles: str):
    """Factory that returns a dependency enforcing one of the given roles."""

    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=get_message("FORBIDDEN"),
            )
        return current_user

    return _check
