"""Auth schemas — login, tokens, current-user read model, and self-service profile."""

import re

from pydantic import BaseModel, field_serializer, field_validator

from app.services.storage import generate_presigned_url


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


class UserMe(BaseModel):
    """Current-user response — never includes password_hash.

    Carries the fields the frontend needs to gate menus/actions: role,
    department/position (from metadata), the effective permission actions,
    and the (presigned) avatar URL.
    """

    id: int
    username: str
    full_name: str
    phone: str | None
    avatar: str | None = None
    role: str
    is_active: bool
    department: str | None
    position: str | None
    employee_code: str | None
    depot_id: int | None
    permissions: list[str]

    @field_serializer("avatar")
    def serialize_avatar(self, avatar: str | None) -> str | None:
        """Presign the stored S3 object key into a temporary URL."""
        if not avatar:
            return avatar
        return generate_presigned_url(avatar) or avatar


class ProfileUpdate(BaseModel):
    """Self-service profile update — the fields a user may change on their own account."""

    full_name: str | None = None
    phone: str | None = None
    avatar: str | None = None  # S3 object key; pass None to remove

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not (1 <= len(v) <= 255):
            raise ValueError("Họ tên phải từ 1 đến 255 ký tự")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.fullmatch(r"^0\d{9}$", v):
            raise ValueError("Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0")
        return v


class ChangePasswordRequest(BaseModel):
    """Request body for a user changing their own password."""

    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Mật khẩu mới phải có ít nhất 6 ký tự")
        return v


class ChangePasswordResponse(BaseModel):
    """Response after a successful self-service password change."""

    message: str
