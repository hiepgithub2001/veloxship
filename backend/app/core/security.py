"""Password hashing and JWT token helpers."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int, username: str) -> str:
    """Create a short-lived JWT access token."""
    return _create_token(
        {"sub": str(user_id), "username": username, "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES),
    )


def create_refresh_token(user_id: int, username: str) -> str:
    """Create a longer-lived JWT refresh token."""
    return _create_token(
        {"sub": str(user_id), "username": username, "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS),
    )


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token. Raises JWTError on failure."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise
