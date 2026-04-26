"""Auth schemas — login, tokens, user read model."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """POST /auth/login request body."""
    username: str
    password: str


class RefreshRequest(BaseModel):
    """POST /auth/refresh request body."""
    refresh_token: str


class TokenPair(BaseModel):
    """Token pair returned on successful auth."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserRead(BaseModel):
    """User response — never includes password_hash."""
    id: int
    username: str
    full_name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}
