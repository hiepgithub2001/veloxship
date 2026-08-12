"""Vehicle schemas — create, update, read, and paginated list."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator

from app.schemas.common import Page


class VehicleCreate(BaseModel):
    """Schema for creating a new vehicle."""

    license_plate: str
    vehicle_type: str
    max_weight_kg: Decimal
    max_volume_m3: Decimal
    latest_depot_id: int | None = None
    driver_id: int | None = None
    status: str | None = None  # defaults to "active" in service

    @field_validator("license_plate")
    @classmethod
    def validate_license_plate(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Biển số xe không được để trống")
        return v.strip()

    @field_validator("vehicle_type")
    @classmethod
    def validate_vehicle_type(cls, v: str) -> str:
        if v not in ("motorcycle", "truck"):
            raise ValueError("Loại xe phải là 'motorcycle' hoặc 'truck'")
        return v

    @field_validator("max_weight_kg")
    @classmethod
    def validate_max_weight_kg(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Tải trọng phải là số dương")
        return v

    @field_validator("max_volume_m3")
    @classmethod
    def validate_max_volume_m3(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Thể tích phải là số dương")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in ("active", "inactive", "maintenance"):
            raise ValueError("Trạng thái phải là 'active', 'inactive', hoặc 'maintenance'")
        return v


class VehicleUpdate(BaseModel):
    """Schema for partial vehicle update."""

    license_plate: str | None = None
    vehicle_type: str | None = None
    max_weight_kg: Decimal | None = None
    max_volume_m3: Decimal | None = None
    latest_depot_id: int | None = None
    driver_id: int | None = None
    status: str | None = None

    @field_validator("license_plate")
    @classmethod
    def validate_license_plate(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Biển số xe không được để trống")
        return v.strip() if v else v

    @field_validator("vehicle_type")
    @classmethod
    def validate_vehicle_type(cls, v: str | None) -> str | None:
        if v is not None and v not in ("motorcycle", "truck"):
            raise ValueError("Loại xe phải là 'motorcycle' hoặc 'truck'")
        return v

    @field_validator("max_weight_kg")
    @classmethod
    def validate_max_weight_kg(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Tải trọng phải là số dương")
        return v

    @field_validator("max_volume_m3")
    @classmethod
    def validate_max_volume_m3(cls, v: Decimal | None) -> Decimal | None:
        if v is not None and v <= 0:
            raise ValueError("Thể tích phải là số dương")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in ("active", "inactive", "maintenance"):
            raise ValueError("Trạng thái phải là 'active', 'inactive', hoặc 'maintenance'")
        return v


class VehicleRead(BaseModel):
    """Schema for vehicle response."""

    id: int
    license_plate: str
    vehicle_type: str
    max_weight_kg: Decimal
    max_volume_m3: Decimal
    driver_id: int | None
    driver_name: str | None
    latest_depot_id: int | None
    depot_name: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VehiclePage(Page[VehicleRead]):
    """Paginated vehicle list response."""

    pass
