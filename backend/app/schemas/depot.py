"""Depot schemas — create, update, read, and paginated list."""

from datetime import datetime

from pydantic import BaseModel, field_validator

from app.schemas.common import Page


class DepotCreate(BaseModel):
    """Schema for creating a new depot."""

    code: str
    name: str
    phone: str
    address_detail: str
    ward_code: str | None = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        import re

        if not re.fullmatch(r"^[A-Z0-9]{3,20}$", v):
            raise ValueError("Mã bưu cục phải gồm 3-20 ký tự in hoa hoặc số")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not (1 <= len(v) <= 255):
            raise ValueError("Tên bưu cục phải từ 1 đến 255 ký tự")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        import re

        if not re.fullmatch(r"^0\d{9}$", v):
            raise ValueError("Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0")
        return v

    @field_validator("address_detail")
    @classmethod
    def validate_address_detail(cls, v: str) -> str:
        if not (1 <= len(v) <= 500):
            raise ValueError("Địa chỉ chi tiết phải từ 1 đến 500 ký tự")
        return v


class DepotUpdate(BaseModel):
    """Schema for partial depot update."""

    name: str | None = None
    phone: str | None = None
    address_detail: str | None = None
    ward_code: str | None = None
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None and not (1 <= len(v) <= 255):
            raise ValueError("Tên bưu cục phải từ 1 đến 255 ký tự")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is not None:
            import re

            if not re.fullmatch(r"^0\d{9}$", v):
                raise ValueError("Số điện thoại phải gồm 10 chữ số, bắt đầu bằng 0")
        return v

    @field_validator("address_detail")
    @classmethod
    def validate_address_detail(cls, v: str | None) -> str | None:
        if v is not None and not (1 <= len(v) <= 500):
            raise ValueError("Địa chỉ chi tiết phải từ 1 đến 500 ký tự")
        return v


class DepotRead(BaseModel):
    """Schema for depot response."""

    id: int
    code: str
    name: str
    phone: str
    address_detail: str
    ward_code: str | None
    ward_name: str | None
    province_code: str | None
    province_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DepotPage(Page[DepotRead]):
    """Paginated depot list response."""

    pass
