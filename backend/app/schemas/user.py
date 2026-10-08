"""User (staff) admin schemas — create, update, read, reset password."""

import re
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.common import Page


def _validate_phone(v: str | None) -> str | None:
    if v is None:
        return v
    if not re.fullmatch(r"^0\d{9}$", v):
        raise ValueError("Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0")
    return v


def _validate_username(v: str) -> str:
    v = v.strip().lower()
    if not re.fullmatch(r"^[a-z0-9._-]{3,50}$", v):
        raise ValueError("Tên đăng nhập phải gồm 3-50 ký tự thường, số hoặc . _ -")
    return v


class UserCreate(BaseModel):
    """Schema for creating a staff account."""

    username: str
    full_name: str
    phone: str | None = None
    password: str | None = None  # omit to auto-generate
    role: str = "operator"
    department: str | None = None
    position: str | None = None
    employee_code: str | None = None
    depot_id: int | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        return _validate_username(v)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if not (1 <= len(v) <= 255):
            raise ValueError("Họ tên phải từ 1 đến 255 ký tự")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        return _validate_phone(v)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Vai trò không được để trống")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if v is not None and len(v) < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự")
        return v


class UserUpdate(BaseModel):
    """Schema for partial staff account update."""

    full_name: str | None = None
    phone: str | None = None
    role: str | None = None
    department: str | None = None
    position: str | None = None
    employee_code: str | None = None
    depot_id: int | None = None
    is_active: bool | None = None

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
        return _validate_phone(v)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Vai trò không được để trống")
        return v


class UserRead(BaseModel):
    """Schema for a staff account response (admin view)."""

    id: int
    username: str
    full_name: str
    phone: str | None
    role: str
    role_name: str | None = None
    department: str | None
    position: str | None
    employee_code: str | None
    depot_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserCreated(UserRead):
    """User response on creation — carries the one-time temporary password."""

    temporary_password: str | None = None


class UserPage(Page[UserRead]):
    """Paginated user list response."""

    pass


class UserOption(BaseModel):
    """Minimal user representation for picker selects (non-admin callers)."""

    id: int
    full_name: str
    username: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserResetPasswordRequest(BaseModel):
    """Request body for resetting a user's password."""

    password: str | None = None  # omit to auto-generate

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if v is not None and len(v) < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự")
        return v


class UserResetPasswordResponse(BaseModel):
    """Response for a password reset — carries the new temporary password."""

    temporary_password: str
