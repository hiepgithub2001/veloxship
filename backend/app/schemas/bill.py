"""Bill schemas — create, read, status, events (aligned to Hoàng Nam DB v1.1)."""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class BillStatus(str, Enum):
    created = "created"
    picked_up = "picked_up"
    in_transit = "in_transit"
    delivered = "delivered"
    returned = "returned"
    cancelled = "cancelled"


class BillParty(BaseModel):
    """Sender/receiver input.

    Either `customer_id` of an existing customer, or inline fields used to
    get-or-create a customer (khách vãng lai).
    """

    customer_id: int | None = None
    name: str
    phone: str | None = None
    address_detail: str | None = None
    province_code: str | None = None
    province_name: str | None = None
    ward_code: str | None = None
    ward_name: str | None = None


class CustomerRef(BaseModel):
    """Customer snapshot used in bill responses (from `customers` + metadata)."""

    id: int
    code: str | None = None
    name: str
    phone: str | None = None
    customer_type: str
    address_detail: str | None = None
    province_code: str | None = None
    province_name: str | None = None
    ward_code: str | None = None
    ward_name: str | None = None


class BillContentLineSchema(BaseModel):
    """A single content line in the bill."""

    line_no: int | None = None
    description: str
    quantity: int
    weight_kg: float
    length_cm: float | None = None
    width_cm: float | None = None
    height_cm: float | None = None

    model_config = {"from_attributes": True}


class FeeBreakdown(BaseModel):
    """Fee breakdown with total validation."""

    fee_main: float = Field(ge=0)
    fee_insurance: float = Field(ge=0)
    fee_other: float = Field(ge=0)
    fee_vat: float = Field(ge=0)
    fee_total: float = Field(ge=0)

    @field_validator("fee_total")
    @classmethod
    def validate_total(cls, v, info):
        data = info.data
        expected = (
            data.get("fee_main", 0)
            + data.get("fee_insurance", 0)
            + data.get("fee_other", 0)
            + data.get("fee_vat", 0)
        )
        if abs(v - expected) > 0.01:
            raise ValueError("Tổng cước không khớp với tổng các khoản.")
        return v


class BillCreate(BaseModel):
    """POST /bills request body."""

    sender: BillParty
    receiver: BillParty
    cargo_type: Literal["document", "goods"]
    service_tier_code: str
    actual_weight_kg: float = Field(ge=0)
    contents: list[BillContentLineSchema]
    is_insurance_required: bool = False
    cod_amount: float = Field(default=0, ge=0)
    fee: FeeBreakdown
    payer: Literal["sender", "receiver"]


class BillStatusUpdate(BaseModel):
    """POST /bills/{id}/status request body."""

    to_status: BillStatus
    delivered_to_name: str | None = None
    cancellation_reason: str | None = None
    note: str | None = None


class BillStatusEventRead(BaseModel):
    """Status event in the response."""

    id: int
    bill_id: int
    from_status: str | None = None
    to_status: str
    note: str | None = None
    changed_by: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BillRead(BaseModel):
    """Full bill response."""

    id: int
    tracking_number: str
    sender: CustomerRef
    receiver: CustomerRef
    cargo_type: str
    service_tier_code: str
    actual_weight_kg: float
    chargeable_weight_kg: float
    is_insurance_required: bool
    cod_amount: float
    contents: list[BillContentLineSchema]
    fee: FeeBreakdown
    payer: str
    status: str
    delivered_at: datetime | None = None
    delivered_to_name: str | None = None
    cancellation_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    print_count: int
    last_printed_at: datetime | None = None
    last_printed_by: int | None = None

    @classmethod
    def from_model(cls, bill):
        """Convert a Bill ORM model to a BillRead schema."""

        def to_customer_ref(customer) -> CustomerRef:
            meta = customer.customer_metadata if customer else None
            return CustomerRef(
                id=customer.id,
                code=customer.code,
                name=customer.name,
                phone=customer.phone,
                customer_type=customer.customer_type,
                address_detail=(meta or {}).get("address_detail"),
                province_code=(meta or {}).get("province_code"),
                province_name=(meta or {}).get("province_name"),
                ward_code=(meta or {}).get("ward_code"),
                ward_name=(meta or {}).get("ward_name"),
            )

        return cls(
            id=bill.id,
            tracking_number=bill.tracking_number,
            sender=to_customer_ref(bill.sender),
            receiver=to_customer_ref(bill.receiver),
            cargo_type=bill.cargo_type,
            service_tier_code=bill.service_tier_code,
            actual_weight_kg=float(bill.actual_weight_kg),
            chargeable_weight_kg=float(bill.chargeable_weight_kg),
            is_insurance_required=bill.is_insurance_required,
            cod_amount=float(bill.cod_amount),
            contents=[
                BillContentLineSchema.model_validate(line) for line in bill.content_lines
            ],
            fee=FeeBreakdown(
                fee_main=float(bill.fee_main),
                fee_insurance=float(bill.fee_insurance),
                fee_other=float(bill.fee_other),
                fee_vat=float(bill.fee_vat),
                fee_total=float(bill.fee_total),
            ),
            payer=bill.payer,
            status=bill.status,
            delivered_at=bill.delivered_at,
            delivered_to_name=bill.delivered_to_name,
            cancellation_reason=bill.cancellation_reason,
            created_at=bill.created_at,
            updated_at=bill.updated_at,
            created_by=bill.created_by,
            updated_by=bill.updated_by,
            print_count=bill.print_count,
            last_printed_at=bill.last_printed_at,
            last_printed_by=bill.last_printed_by,
        )


class BillPage(BaseModel):
    """Paginated bill list response."""

    items: list[BillRead]
    page: int
    page_size: int
    total: int
