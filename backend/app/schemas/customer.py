"""Customer schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import Page

# Customer segmentation. The `customers.customer_type` column has no DB CHECK
# constraint, so this Literal is the single source of truth for valid values.
CustomerType = Literal["retail", "shop", "enterprise"]

# Profile fields stored inside the `customers.metadata` JSONB column. Keeping
# the address there means the customer module needs no schema migration.
ADDRESS_FIELDS: tuple[str, ...] = (
    "address_detail",
    "province_code",
    "province_name",
    "ward_code",
    "ward_name",
)


class CustomerCreate(BaseModel):
    """Create a customer (khách hàng gửi/nhận, kể cả khách vãng lai)."""

    name: str = Field(min_length=1)
    phone: str | None = None
    customer_type: CustomerType = "retail"
    address_detail: str | None = None
    province_code: str | None = None
    province_name: str | None = None
    ward_code: str | None = None
    ward_name: str | None = None
    # Contact person behind `phone` — populated by the Excel importer, which
    # splits a two-person "Liên hệ" cell; empty for manually created profiles.
    contact_name: str | None = None
    contact_raw: str | None = None


class CustomerUpdate(BaseModel):
    """Partial update for a customer profile.

    Address fields are flattened into `metadata` JSONB, mirroring
    `CustomerCreate`. `code` is generated once and intentionally immutable, so
    it is absent from this schema.
    """

    name: str | None = Field(default=None, min_length=1)
    phone: str | None = None
    customer_type: CustomerType | None = None
    address_detail: str | None = None
    province_code: str | None = None
    province_name: str | None = None
    ward_code: str | None = None
    ward_name: str | None = None
    is_active: bool | None = None


class CustomerRead(BaseModel):
    """Customer response.

    Address fields are also exposed flattened (read from `metadata`) so the
    edit form does not have to know about the JSONB layout.
    """

    id: int
    code: str | None = None
    name: str
    phone: str | None = None
    customer_type: str
    metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias="customer_metadata",
    )
    is_active: bool
    created_at: datetime
    updated_at: datetime

    address_detail: str | None = None
    province_code: str | None = None
    province_name: str | None = None
    ward_code: str | None = None
    ward_name: str | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}

    @model_validator(mode="after")
    def _flatten_address(self):
        """Copy address keys out of `metadata` when not already set."""
        metadata = self.metadata or {}
        for field in ADDRESS_FIELDS:
            if getattr(self, field) is None:
                setattr(self, field, metadata.get(field))
        return self


class CustomerMetrics(BaseModel):
    """Headline activity metrics for one customer.

    `total_bills` counts every bill where the customer is sender OR receiver.
    `total_revenue` counts each bill once and only when the customer is the
    sender, so a customer appearing on both sides cannot inflate revenue.

    Money is `Decimal`, which Pydantic serializes as a JSON string — callers
    must parse it rather than relying on float coercion.
    """

    total_bills: int
    total_revenue: Decimal
    delivered_bills: int
    cancelled_bills: int
    first_bill_at: datetime | None = None
    last_bill_at: datetime | None = None


class CustomerPage(Page[CustomerRead]):
    """Paginated customer directory response."""

    pass
