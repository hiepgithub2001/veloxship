"""Permission schemas — dynamic roles, role permissions, and the action catalogue."""

import re

from pydantic import BaseModel, field_validator

from app.core.permissions import is_valid_action

_ROLE_CODE_RE = re.compile(r"^[a-z][a-z0-9_]{1,49}$")


class RoleCreate(BaseModel):
    """Schema for creating a new role."""

    code: str
    name: str
    description: str | None = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        v = v.strip().lower()
        if not _ROLE_CODE_RE.fullmatch(v):
            raise ValueError(
                "Mã vai trò phải gồm 2-50 ký tự thường, số hoặc _, bắt đầu bằng chữ cái"
            )
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not (1 <= len(v) <= 100):
            raise ValueError("Tên vai trò phải từ 1 đến 100 ký tự")
        return v


class RoleUpdate(BaseModel):
    """Schema for partial role update — code is immutable."""

    name: str | None = None
    description: str | None = None
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not (1 <= len(v) <= 100):
            raise ValueError("Tên vai trò phải từ 1 đến 100 ký tự")
        return v


class RoleRead(BaseModel):
    """Schema for a role response — includes its granted actions and user count."""

    code: str
    name: str
    description: str | None
    is_active: bool
    actions: list[str] = []
    user_count: int = 0

    @field_validator("actions", mode="before")
    @classmethod
    def _flatten_actions(cls, v: list) -> list[str]:
        """Accept either `RolePermission` ORM objects or plain strings."""
        return [a.action if hasattr(a, "action") else a for a in v]


class RolePermissionsUpdate(BaseModel):
    """Schema for replacing a role's granted actions."""

    actions: list[str]

    @field_validator("actions")
    @classmethod
    def validate_actions(cls, v: list[str]) -> list[str]:
        for action in v:
            if not is_valid_action(action):
                raise ValueError(f"Quyền không hợp lệ: {action}")
        return v


class PermissionActionItem(BaseModel):
    """A single assignable action in the catalogue."""

    code: str
    label: str


class PermissionCatalogModule(BaseModel):
    """A business module grouping assignable actions."""

    code: str
    label: str
    actions: list[PermissionActionItem]


class PermissionCatalogRead(BaseModel):
    """Catalogue of every assignable action, grouped by module."""

    modules: list[PermissionCatalogModule]
