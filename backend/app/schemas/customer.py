"""Customer schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class CustomerCreate(BaseModel):
    """Create a customer (khách hàng gửi/nhận, kể cả khách vãng lai)."""

    name: str
    phone: str | None = None
    customer_type: str = "retail"
    address_detail: str | None = None
    province_code: str | None = None
    province_name: str | None = None
    ward_code: str | None = None
    ward_name: str | None = None


class CustomerRead(BaseModel):
    """Customer response."""

    id: int
    code: str | None = None
    name: str
    phone: str | None = None
    customer_type: str
    metadata: dict[str, Any] | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
