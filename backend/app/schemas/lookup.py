"""Shared schemas for department / position lookup lists stored in user metadata."""

from pydantic import BaseModel, field_validator


class LookupItem(BaseModel):
    """A distinct department/position value and how many users use it."""

    name: str
    user_count: int


class LookupList(BaseModel):
    """List of distinct department/position values."""

    items: list[LookupItem]
    total: int


class LookupRename(BaseModel):
    """Rename request — `name` is the new value; the old value is the path param."""

    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not (1 <= len(v) <= 255):
            raise ValueError("Tên phải từ 1 đến 255 ký tự")
        return v
